import picamera
import base64
import json
import time
import configparser

from tornado import gen, ioloop
from mqtt_base import MQTTBase, logIt

@gen.coroutine
def main():

    mqtt_topic = 'mqtt_topic'
    topic_prefix = config.get(mqtt_config, 'topic_prefix')
    instance_id = config.get(mqtt_topic, 'id')
    instance_name = config.get(mqtt_topic, 'name')

    yield gen.sleep(2.0)

    with picamera.PiCamera() as camera:
        camera.resolution = (752, 480)
        camera.start_preview()

        for n in range(5):
            tstamp = int(time.time())

            fn = 'images/image_{0:04d}.jpg'.format(n)
            camera.capture(fn)

            with open(fn, "rb") as image_file:
                img = base64.b64encode(image_file.read())

                dd = dict(ts=tstamp, seq=n, source=instance_name, img=img, velocity=100, plate='TESTE')
                payload = json.dumps(dd)

                mqtt_client.publish("{0}/{1:03d}/image".format(topic_prefix, instance_id), payload)
                logIt('Capture sent %d' % n)

            yield gen.sleep(2.0)

        camera.stop_preview()
        camera.close()

    logIt('Exiting...')


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('camera.ini')

    mqtt_config = 'mqtt_config'
    client_id = config.get(mqtt_config, 'client_id')
    server = config.get(mqtt_config, 'server')
    port = config.getint(mqtt_config, 'port')
    keepalive = config.getint(mqtt_config, 'keepalive')
    username = config.get(mqtt_config, 'username')
    password = config.get(mqtt_config, 'password')
    ca_cert = config.get(mqtt_config, 'ca_cert')

    mqtt_client = MQTTBase(client_id, [], server, port, keepalive, username, password, ca_cert)
    mqtt_client.connect()
    ioloop.PeriodicCallback(mqtt_client.loop, 10).start()    # 10 ms
    ioloop.IOLoop.current().run_sync(main)
