import re, sys, argparse
from subprocess import check_output, Popen, PIPE
import traceback

class ExperimentParser:
    def __init__(self, args):
        self.capFiles = []
        self.goodputs = []
        self.resultsDir = args.directory
        self.testfile_blocks = args.testfileblocks
        self.chunk_size = args.chunksize

    def genStatistics(self):
        try:
            print("Generating statistics...")
            self.goodputs = self.parseStations()
            if len(self.goodputs) == 0:
                 raise RuntimeError("No goodput results found!")
            capFilesTemp = check_output(["find", self.resultsDir, "-name", "*-cap"]).decode().split("\n")
            self.capFiles = capFilesTemp[0:len(capFilesTemp) -1]
            for capFile in self.capFiles:
                bytesTrans_tuple = self.parseCap(capFile)
                bytesTrans = bytesTrans_tuple[0] + bytesTrans_tuple[1] + bytesTrans_tuple[2]
                ip_bytes = bytesTrans_tuple[4]
                totalSize = self.testfile_blocks * self.chunk_size
                gpEfficiency = totalSize * len(self.goodputs) * 1.0 / bytesTrans
                print("Goodput Efficiency: ",  gpEfficiency)
                with open(capFile + "-results", "w") as f:
                    msgInteg = self.getMessageIntegrity()
                    if msgInteg:
                        f.write(msgInteg)
                    count = 1
                    gpStations = []
                    for gp in self.goodputs:
                        #gp = station.cmd('grep -r "Goodput:" | cut -d " " -f 2,3')
                        if "kbit/s" in gp:
                            gpVal = float(gp.split("kbit/s")[0]) * 0.001
                            gp = str(gpVal) + " Mbit/s"
                        f.write("Sta{} goodput: {}\n".format(count, gp))
                        gpStations.append(float(gp.split(" ")[0]))
                        count += 1
                    avgGoodput = sum(gpStations) / len(gpStations)
                    #avgThroughput = avgGoodput / gpEfficiency
                    avgThroughput = ((bytesTrans / bytesTrans_tuple[3]) / 1000000.0) * 8 #convert to Mbps
                    medianPosA = int(len(gpStations) / 2) - 1
                    medianGoodput = ""
                    sortedStations = sorted(gpStations)
                    if len(gpStations) % 2 == 0:
                        medianGoodput = (sortedStations[medianPosA] + sortedStations[medianPosA + 1]) / 2
                    else:
                        medianGoodput = sortedStations[medianPosA]
                    f.write("Min goodput: {} (Mbps)\nMax goodput: {} (Mbps)\nMedian goodput: {} (Mbps)\nAvg goodput: {} (Mbps)\nTotal interest bytes: {}\nTotal data bytes: {}\nTotal nack bytes: {}\nGoodput efficiency: {}\nAvg throughput: {} (Mbps)\nTime Taken: {}\n".format(min(gpStations), max (gpStations), medianGoodput, avgGoodput, bytesTrans_tuple[0],  bytesTrans_tuple[1], bytesTrans_tuple[2], str(gpEfficiency * 100.0) + "%", avgThroughput, bytesTrans_tuple[3]))
                    with open("{}/ip-key".format(self.resultsDir), "r") as ip_file:
                        ip_station_dict = {"224.0.23.170":"multicast"}
                        for line in ip_file.readlines():
                            ip, name = line.strip().split(":")
                            ip_station_dict[ip] = name
                        throughput_sum = 0
                        upstream_sum = 0
                        downstream_sum = 0
                        for i in ip_bytes:
                            ip_throughput = (((ip_bytes[i][0] + ip_bytes[i][1]) / bytesTrans_tuple[3]) / 1000000.0) * 8
                            upstream_throughput = (((ip_bytes[i][0]) / bytesTrans_tuple[3]) / 1000000.0) * 8
                            downstream_throughput = (((ip_bytes[i][1]) / bytesTrans_tuple[3]) / 1000000.0) * 8
                            throughput_sum += ip_throughput
                            upstream_sum += upstream_throughput
                            downstream_sum += downstream_throughput
                            f.write("{}: {} {} {}\n".format(ip_station_dict[i], ip_throughput, upstream_throughput, downstream_throughput))
                        f.write("Avg. Throughput: " + str(ip_throughput  / len(ip_bytes)) + "\n")
                        f.write("Avg. Upstream Throughput: " + str(upstream_sum / len(ip_bytes)) + "\n")
                        f.write("Avg. Downstream Throughput: " + str(downstream_sum / len(ip_bytes)) + "\n")
        except IOError as e:
            print("ERROR DURING genStatistics: ", e)
            sys.exit(1)

    def parseCap(self, capFile):
        ''' Parse tshark capture file to determine NDN interest and data bytes '''
        tsharkOutput = check_output(["tshark", "-2", "-l", "-X", "lua_script:/usr/local/share/ndn-dissect-wireshark/ndn.lua", "-r", capFile])
        interestBytes = 0
        dataBytes = 0
        nackBytes = 0
        packetVals = dict()
        ip_bytes = dict()
        end = -1
        for line in tsharkOutput.splitlines():
            temp_line = re.sub(' +',' ',line)
            strips = temp_line.strip().split(" ")
            packetNum = strips[0]
            end = float(strips[1])
            #print(packetNum)
            if "Reassembled in" in line:
                tempBytes = int(line.split("Fragmented")[0].split(" ")[-2])
                finalPacket = line.split(" ")[-1].strip("]").strip("#")
                if finalPacket in packetVals:
                    packetVals[finalPacket] = packetVals[finalPacket] + tempBytes
                else:
                    packetVals[finalPacket] = tempBytes
            if "(NDN)" in line:
                tempBytes = int(line.split("(NDN)")[1].split(" ")[1])
        #Sending node- upstream
                if strips[2] in ip_bytes:
                    ip_bytes[strips[2]][0] += tempBytes
                else:
                    ip_bytes[strips[2]] = [0,0]
                    ip_bytes[strips[2]][0] += tempBytes
                #Recieving node- downstream
                if strips[4] in ip_bytes:
                    ip_bytes[strips[4]][1] += tempBytes
                else:
                    ip_bytes[strips[4]] = [0,0]
                    ip_bytes[strips[4]][1] += tempBytes
                if packetNum in packetVals:
                    tempBytes += packetVals[packetNum]
                    #print(packetNum + ":" + str(tempBytes))
                if "Interest" in line:
                    interestBytes += tempBytes
                elif "Data" in line:
                    dataBytes += tempBytes
                elif "Nack" in line:
                    nackBytes += tempBytes
        print("Interests: {}\nData: {}\nTime: {}".format(interestBytes, dataBytes,end))
        return (interestBytes, dataBytes, nackBytes, end, ip_bytes)

    def parseStations(self):
        try:
            grepStaStr = check_output(['sudo', 'grep', '-r', 'Goodput:', self.resultsDir]).decode()
            staList = [i for i in grepStaStr.split("\n") if "Goodput:" in i]
            sortedStaList = sorted(staList, key=lambda gp: int(re.search("(?<=sta)[0-9]+(?=/chunks)", gp).group(0)))
            return [i.split("Goodput: ")[1] for i in sortedStaList]
        except Exception as e:
            traceback.print_exc()
            print("ERROR DURING parseStations: ", e)
            sys.exit()

    def getMessageIntegrity(self):
        try:
            for dataFile in ["chunksfile", "testfile"]:
                ps = Popen(('find', self.resultsDir, '-name',  'chunksfile', '-exec', 'sha1sum', '{}', '+' ), stdout=PIPE)
                output = check_output(('cut', '-d', ' ', '-f', '1'), stdin=ps.stdout).decode().split("\n")
                ps.wait()
                if dataFile == "chunksfile":
                    chunksHashes = output[0:len(output) -1]
                else:
                    testHash = output[0]
            hasMsgIntegrity = all(testHash == chunkshash for chunkshash in chunksHashes)
            chunksHashesNumbered = [str(i + 1) + ") " + chunksHashes[i] for i in range(len(chunksHashes))]
            return "The testfile hash: {}\nThe chunksfile hashes:\n{}\nMessage Integrity Result: {}\n\n".format(testHash, "\n".join(chunksHashesNumbered), hasMsgIntegrity)
        except Exception as e:
            print("ERROR DURING getMessageIntegrity: ", e)
            return None

def main():
    p = ExperimentParser(args)
    p.genStatistics()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--testfileblocks", type=int, default=10000,
                        help="Number of testfile blocks")
    parser.add_argument("-s", "--chunksize", type=int, default=4400,
                        help="Size of chunks")
    parser.add_argument("-d", "--directory", default=".",
                        help="Location of the experiment directory")
    args = parser.parse_args()
    main()
