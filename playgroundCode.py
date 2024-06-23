import socket
import struct
import time


def request_arc_data(sock):
    with open("arc_data_request.hex", 'rb') as file:
        arc_data_request = file.read()
    sock.sendall(arc_data_request)
    return


if __name__ == '__main__':
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(('192.168.1.6', 30031))
    request_arc_data(clientSocket)
    buffer = b''
    timeout_counter = 0
    timeout_thresh = 5
    try:
        while True:
            data = clientSocket.recv(1024)
            if not data:
                timeout_counter += 1
                if timeout_counter > timeout_thresh:
                    break
                time.sleep(0.1)
                continue
            timeout_counter = 0
            buffer += data
            idx = 0
            while idx < len(buffer) - 11:  # at least one header and a byte existing in data.
                header = struct.unpack('<I', buffer[idx:idx + 4])
                if header == struct.unpack('<I', b'\xEE\xFF\xEE\xFF'):
                    sens_id, msg_type, msg_len = struct.unpack('<HcI', buffer[idx + 4: idx + 11])
                    print(f"Message Length: {msg_len} and buffer length: {len(buffer)}")
                    # check if the complete message is in the buffer
                    if len(buffer[idx:]) < 11 + msg_len:
                        break
                    if msg_type == b'\x0A':
                        print(f"sens_id: {sens_id}, msg_type: {msg_type}, msg_len: {msg_len}")
                        print("Analyzing the ARC message!")
                        azimuth, elevation, rad_mode, resolution, use_zip_algorithm = struct.unpack(
                            "<HHcIc", buffer[idx + 11: idx + 11 + 10])
                        print(f"azimuth: {azimuth / 100}")
                        print(f"elevation: {elevation / 100}")
                        print(f"resolution: {resolution / 1000}")
                        arc_data_len = struct.unpack('>H', buffer[idx + 11 + 10: idx + 11 + 12])[0]
                        print(f"arc_data_len: {arc_data_len}")
                        arc_data = []
                        for arc in struct.unpack(f"{msg_len - 12 - 4}c", buffer[idx + 11 + 12: idx + 11 + msg_len - 4]):
                            arc_data.append(arc.hex())
                        print(f"Arc vector length: {len(arc_data)}")
                        print(f"arc_data: {arc_data}")
                    idx += 11 + msg_len
                else:
                    idx += 1
            buffer = buffer[idx:]

    except KeyboardInterrupt:
        print("Program Stopped by keyboard interrupt")
    except Exception as e:
        print(e)
    finally:
        print("Closing socket")
        clientSocket.close()
