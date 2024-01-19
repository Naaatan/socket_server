import random
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from dataclasses_json import config, dataclass_json

self_ip = "0.0.0.0"
send_ip = "xxx.xx.x.xxx"
port = 23456
is_broadcast = False

# socket.SOCK_STREAM ::: TCP
# socket.SOCK_DGRAM  ::: UDP
socket_protcol_type = socket.SOCK_DGRAM


@dataclass_json
@dataclass
class GpsTag:
    no: int
    latitude: float
    longitude: float
    speed: float = field(metadata=config(field_name="speed[cm/sec]"))
    time_stamp: str

    def simple(self) -> str:
        return "[ No.{no} (lat,lng)={lat}, {lng} time={time}]".format(
            no=self.no, lat=self.latitude, lng=self.longitude, time=self.time_stamp
        )


@dataclass_json
@dataclass
class Tags:
    data: List[GpsTag] = None

    def simple(self) -> str:
        return ",".join([d.simple() for d in self.data])


def make_sample_data(count: int) -> Tags:
    tags = Tags()
    tags.data = [make_sample_gps_tag(no=i, count=count) for i in range(1, 6)]
    return tags


def make_sample_gps_tag(no: int, count: int) -> GpsTag:
    base_lat = 34.715975
    base_lng = 137.776841
    latlng_array = [
        (34.716441, 137.777121),
        (34.716359, 137.777300),
        (34.7163533, 137.7784529),
        (34.716681, 137.776867),
        (34.7166474, 137.7755423),
        (34.715921, 137.776294),
        (34.7151392, 137.7768912),
        (34.715468, 137.777744),
        (34.715332, 137.778581),
        (34.716593, 137.779388),
    ]

    return GpsTag(
        no=no,
        latitude=base_lat if count == 0 else random.choice(latlng_array)[0],
        longitude=base_lng if count == 0 else random.choice(latlng_array)[1],
        speed=random.uniform(3, 70),
        time_stamp=datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M:%S"),
    )


def start():
    if socket_protcol_type == socket.SOCK_DGRAM:
        start_udp(is_broadcast=is_broadcast)
    elif socket_protcol_type == socket.SOCK_STREAM:
        start_tcp()
    else:
        print("socket ptotcol type is unknown... bye.")


def start_tcp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpSocket:
        # サーバーを立ち上げる
        tcpSocket.bind((self_ip, port))
        print("Bind   : Ip=[{ip}] Port=[{port}]".format(ip=self_ip, port=port))

        # 1クライアントだけ受け入れる(TCP)
        tcpSocket.listen(1)

        # クライアントからの接続待ち(TCP)
        clientSocket, addr = tcpSocket.accept()
        print("Accept : clientIp=[{ip}]".format(ip=addr))

        count = 1
        while True:
            barrel_data = make_sample_data(count=count)
            message = barrel_data.to_json(indent=4, ensure_ascii=False)

            try:
                # クライアントへメッセージ送信(TCP)
                clientSocket.sendall(message.encode("utf-8"))

                print_message = barrel_data.simple()
                print("Send   : {}".format(print_message))
                time.sleep(3)
                count += 1
            except Exception as e:
                print("Send   : {}".format(e))
                time.sleep(3)


def start_udp(is_broadcast: bool):
    udp_send_ip = send_ip

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udpSocket:
        # サーバーを立ち上げる
        # udpSocket.bind((self_ip, port))
        print("Bind   : Ip=[{ip}] Port=[{port}]".format(ip=self_ip, port=port))

        # ブロードキャスト設定
        if is_broadcast:
            udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_send_ip = "<broadcast>"

        count = 0
        while True:
            barrel_data = make_sample_data(count=count)
            message = barrel_data.to_json(indent=4, ensure_ascii=False)

            try:
                # クライアントへメッセージ送信(UDP)
                udpSocket.sendto(message.encode("utf-8"), (udp_send_ip, port))

                print_message = barrel_data.simple()
                print("Send   : {}".format(print_message))
                time.sleep(10)
                count += 1
            except Exception as e:
                print("Send   : {}".format(e))
                time.sleep(3)


if __name__ == "__main__":
    start()
