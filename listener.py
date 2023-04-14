from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib2
import logging
import json

class SiriServer(BaseHTTPRequestHandler):
    def do_POST(self):
        logging.info("Received request: %s %s" % (self.command, self.path))
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        logging.info("Content-Type: %s" % content_type)
        logging.info("Content-Length: %s" % content_length)
        post_data = self.rfile.read(content_length)
        logging.info("Request data: %s" % post_data)

        # Send the audio file to Google's servers
        url = "https://www.google.com/speech-api/v2/recognize?output=json&lang=en-US&key=YOUR_API_KEY"
        headers = {'Content-Type': 'audio/x-flac; rate=16000'}
        try:
            request = urllib2.Request(url, post_data, headers)
            response = urllib2.urlopen(request, timeout=10)
        except urllib2.HTTPError as e:
            logging.error("Failed to send request to Google: %s" % e)
            self.send_error(400, 'Bad Request: %s' % e)
            return

        # Write the response to a file
        response_data = response.read()
        with open('response.txt', 'w') as f:
            f.write(response_data)

        # Read the transcript from the response file
        with open('response.txt', 'r') as f:
            response_data = f.read().strip()
            transcript = ''
            for line in response_data.split('\n'):
                try:
                    google_response = json.loads(line)
                    if 'result' in google_response and len(google_response['result']) > 0:
                        transcript = google_response['result'][0]['alternative'][0]['transcript']
                        break
                except (KeyError, ValueError) as e:
                    logging.error("Failed to parse response from Google: %s" % e)
                    continue

        # Send the transcript back as a response
        response_string = '{{"status":0,"id":"someid","hypotheses":[{{"utterance":"{transcript}","confidence":0.97}}]}}'.format(transcript=transcript)
        logging.info("Returning response string: %s" % response_string)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response_string.encode())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        server_address = ('', 80)
        httpd = HTTPServer(server_address, SiriServer)
        logging.info('Siri server is running on port 80...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
        logging.info('Siri server stopped.')
