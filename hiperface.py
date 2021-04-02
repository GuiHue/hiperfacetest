from crccheck.checksum import ChecksumXor8
import serial, time, binascii

# Basic Script to read position from Hiperface encoders using RS485
# Provides a basic Function to read positions and scrambled code to send arbitrary commands.
# Sorry, I'm a python noob and haven't botherd with clases...

#initialization and open the port
ser = serial.Serial()
# Choose based on your system/ linux will have sth. like /dev/ttty...
ser.port = "COM4"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_EVEN #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
ser.timeout = None          #block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 0.2     #timeout for write

def readPosition(numberReps, updateRate=0.2):
    data = bytearray.fromhex("5042")
    data.append(ChecksumXor8.calc(data))
    print ('Attempting to make ', numberReps, ' read attemps with intervall of ', updateRate, ' seconds')
    try: 
        ser.open()
    except Exception as e:
        print ("error open serial port: " + str(e))
        exit()
    if ser.isOpen():
        try:
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput()#flush output buffer, aborting current output 
            # ser.write(data)
            # time.sleep(0.010)  #give the serial port sometime to receive the data
            numOfLines = 1
            while True:
                ser.write(data)
                time.sleep(0.01)
                response = ser.read(7)
                print('>> Cycle #' + str(numOfLines))
                print('Response raw:', binascii.hexlify(response))
                position=int.from_bytes(response[2:6],'big',signed=False)
                print ('Absolute Position 32bit unsigned:', position)
                print('>> End cycle')
                numOfLines = numOfLines + 1
                time.sleep(updateRate)
                if (numOfLines >= numberReps+1):
                    break
            ser.close()
            print ('>> Finished reading')
        except Exception as e1:
            print ("error communicating...: " + str(e1))
    else:
        print ("cannot open serial port ")

# Read position

readPosition(10, 0.2)

#
#   Manual Mode
#

# Enter adress of encoder: 40 is default, FF is broadcast - current encoder: 50
adr = bytearray.fromhex("FF")
# Enter command as per list of hiperface commands (52 is status, 42 read position) 
# See hiperface spec for details
# #  https://cdn.sick.com/media/docs/5/65/865/operating_instructions_specification_hiperface%C2%AE_motor_feedback_protocol_en_im0064865.pdf
cmd = bytearray.fromhex("52")
# Enter masterdata if required (code, register requests), otherwise leave empty
masterData = bytearray.fromhex("")
data = adr + cmd + masterData
data.append(ChecksumXor8.calc(data))
# Enter the number of payload bytes you expect
# value is increased by 3 to account for adress, command ACK and checksum
readNumberOfBytes = 4
readNumberOfBytes += 3
# Sleep time before response is read
sleepTime=0.01

try: 
    ser.open()
except Exception as e:
    print ("error open serial port: " + str(e))
    exit()
if ser.isOpen():
    try:
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output 
        numOfLines = 0
        while True:
            print('>> Start cycle')
            ser.write(data)
            time.sleep(sleepTime)
            response = ser.read(readNumberOfBytes)
            print(binascii.hexlify(response))
            # Note that some slave answers include INT values of varying bit length within response. Configure the required bits, big/little endian and signed to your liking
            # position=int.from_bytes(response[2:6],'big',signed=False)
            # print (position)
            print('>> End cycle')
            numOfLines = numOfLines + 1
            # Timer before new cycle is started
            time.sleep(0.5)
            # Integer value to limit number of iterations
            if (numOfLines >= 5):
                break
        ser.close()
    except Exception as e1:
        print ("error communicating...: " + str(e1))
else:
    print ("cannot open serial port ")


