import re

class GPSData:
    def __init__(self):
        self.system_info = {}
        self.device_position = {}
        self.satellite_data = {}

    def update_data(self, sentence):
        if not sentence.strip() or not sentence.startswith('$'):
            if sentence == '':
                pass
            else:
                print(f"Ignorowana linia (niepoprawny początek lub pusta): {sentence}")
            return
        if self.validate_checksum(sentence):
            parsed_data = self.parse_nmea_sentence(sentence)
            if parsed_data:
                header = parsed_data['header']
                values = parsed_data['values']
                checksum = parsed_data['checksum']
                self.process_data(header, values, checksum)
            else:
                print(f"Nieznana sekwencja: {sentence}")
        else:
            print(f"Suma kontrolna niepoprawna dla sekwencji: {sentence}")

    def validate_checksum(self, sentence):
        if '*' not in sentence:
            return False
        sentence_without_checksum, checksum = sentence.strip().split('*')
        calculated_checksum = 0
        for char in sentence_without_checksum[1:]:
            calculated_checksum ^= ord(char)
        return f"{calculated_checksum:X}" == checksum.upper()

    def parse_nmea_sentence(self, sentence):
        parts = sentence.strip().split('*')[0].split(',')
        if re.match(r"^\$(GP|GL|GA|GB)(GGA|RMC|GSA|GSV|GLL|VTG)", parts[0]):
            header = parts[0][3:]  # Extract the message type only
            return {'header': header, 'values': parts[1:], 'checksum': sentence.split('*')[1] if '*' in sentence else ''}
        else:
            return None

    def process_data(self, header, values, checksum):
        try:
            if header == 'GGA':
                self.device_position.update({
                    'Czas': values[0],
                    'Szerokość geograficzna': f"{values[1]} {values[2]}",
                    'Dlugosc geograficzna': f"{values[3]} {values[4]}",
                    'Jakość pomiaru': values[5],
                    'Liczba śledzonych satelitów': values[6],
                    'Precyzja horyzontalna': values[7],
                    'Wysokość n.p.m.': f"{values[8]} {values[9]}",
                    'Wysokość geoid ': f"{values[10]} {values[11]}"
                })
            elif header == 'GLL':
                self.device_position.update({
                    'Szerokość geograficzna': f"{values[0]} {values[1]}",
                    'Dlugosc geograficzna': f"{values[2]} {values[3]}",
                    'Czas': values[4],
                    'Status urzadzenia': values[5]
                })
            elif header == 'GSA':
                self.device_position.update({
                    'Sposób określenia pozycji': values[0],
                    'Numery satelitów do pozycjonowania': values[2:14],
                    'Precyzja (ogólnie)': values[14],
                    'Precyzja horyzontalna': values[15],
                    'Precyzja wertykalna': values[16]
                })
            elif header == 'GSV':
                num_of_msgs = int(values[0])
                msg_num = int(values[1])
                satellites_visible = int(values[2])
                if msg_num == 1:
                    self.satellite_data['Liczba widocznych satelitów'] = []
                start = 3
                while start + 3 < len(values):
                    satellite_info = {
                        'ID satelity (numer)': values[start],
                        'Wyniesienie nad równik (w stopniach)': values[start+1],
                        'Azymut satelity (w stopniach)': values[start+2],
                        'SNR': values[start+3]
                    }
                    self.satellite_data['Liczba widocznych satelitów'].append(satellite_info)
                    start += 4
            elif header == 'RMC':
                self.device_position.update({
                    'Czas(UTC)': values[0],
                    'Status urzadzenia': values[1],
                    'Szerokość geograficzna': f"{values[2]} {values[3]}",
                    'Dlugosc geograficzna': f"{values[4]} {values[5]}",
                    'Predkosc': values[6],
                    'Kąt przemieszczania się': values[7],
                    'Data': values[8],
                    'Odchylenie magnetyczne Ziemi': f"{values[9]} {values[10]}"
                })
            elif header == 'VTG':
                self.device_position.update({
                    'Kąt przemieszczania się (True)': f"{values[0]} {values[1]}",
                    'Kąt przemieszczania się (Magnetic)': f"{values[2]} {values[3]}",
                    'Predkosc (wezly)': values[4],
                    'Predkosc (Km/h)': values[5]
                })
            self.system_info['Suma kontrolna'] = checksum
        except IndexError as e:
            print(f"Error processing {header}: {e}, values: {values}")

    def read_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = file.read().strip()
                lines = data.split('\n')
                for line in lines:
                    self.update_data(line.strip())
        except FileNotFoundError:
            print(f"Plik {filename} nie został znaleziony.")


gps_data = GPSData()
gps_data.read_from_file('test.txt')

print("Informacje systemowe:", gps_data.system_info)
print("Pozycja urządzenia:", gps_data.device_position)
print("Dane o satelitach:", gps_data.satellite_data)