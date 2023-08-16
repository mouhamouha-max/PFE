from django.shortcuts import render, redirect
from os.path import join
from pcap_analysis_backend import settings
import uuid
from scapy.all import rdpcap
import scapy.layers.http as http
from scapy.utils import hexdump
import binascii
from scapy.all import *
from datetime import datetime
from django.utils import timezone
import re
from .forms import PacketFilterForm
import re
from datetime import datetime

def extract_sip_info(packet):
    packet_time = packet.time
    
    sip_info = {
        'src_ip': packet[IP].src,
        'dst_ip': packet[IP].dst,
        'method': None,
        'from': None,
        'to': None,
        'headers': None,
        'body': None,
        'summary': None,
        'time': packet_time,  # Ajout du champ 'time'
        'arrival_time': None,  # Ajout du champ 'arrival_time'
    }

    hex_content = binascii.hexlify(packet.load).decode('utf-8')
    
    # Utiliser une expression régulière pour extraire l'heure d'arrivée du texte
    arrival_time_match = re.search(r'Arrival Time: (.*?)[\r\n]', hex_content)
    if arrival_time_match:
        arrival_time_str = arrival_time_match.group(1)
        sip_info['arrival_time'] = datetime.strptime(arrival_time_str, '%b %d, %Y %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')

    if 'UDP' in packet and packet['UDP'].dport == 5060:
        try:
            sip = packet['UDP']['Raw'].load.decode('utf-8')
            sip_info['method'] = sip.split(' ')[0]

            from_match = re.search(r'From:(.*?)\r\n', sip, re.IGNORECASE | re.DOTALL)
            to_match = re.search(r'To:(.*?)\r\n', sip, re.IGNORECASE | re.DOTALL)

            if from_match:
                sip_info['from'] = from_match.group(1).strip()

            if to_match:
                sip_info['to'] = to_match.group(1).strip()

            sip_headers, sip_body = sip.split('\r\n\r\n', 1)
            sip_info['headers'] = sip_headers
            sip_info['body'] = sip_body

            summary_parts = []
            if sip_info['method']:
                summary_parts.append(f"Method: {sip_info['method']}")
            if sip_info['from']:
                summary_parts.append(f"From: {sip_info['from']}")
            if sip_info['to']:
                summary_parts.append(f"To: {sip_info['to']}")

            sip_info['summary'] = ", ".join(summary_parts)

        except Exception as e:
            print("Error while extracting SIP info:", e)

    return sip_info







def analyze_pcap(file_path, from_value=None, to_value=None):
    packets = rdpcap(file_path)

    packet_count = len(packets)

    packet_details = []
    found_packets = False

    for i, packet in enumerate(packets, start=1):
        hex_content = binascii.hexlify(packet.load).decode('utf-8')
        sip_info = extract_sip_info(packet)  # Extract SIP info

        # Get only the phone number from "From" and "To" values (without "sip:") and convert to lowercase
        from_phone = sip_info['from'].split(':')[1].split('@')[0].lstrip('+').lower() if sip_info['from'] else None
        to_phone = sip_info['to'].split(':')[1].split('@')[0].lstrip('+').lower() if sip_info['to'] else None

        # Check if "From" and "To" values match the specified phone numbers
        if from_value and from_phone != from_value:
            continue
        if to_value and to_phone != to_value:
            continue

        packet_detail = {
            'packet_number': i,
            'sip_info': sip_info,  # Add SIP info to packet detail
             'time': sip_info.get('time', None), 
        }
        packet_details.append(packet_detail)
        found_packets = True

    if not found_packets:
        return {'error': 'No packets matching the filter found.'}

    results = {
        'packet_count': packet_count,
        'packet_details': packet_details,
    }

    return results


from .forms import PacketFilterForm



def upload_pcap_file(request):
    if request.method == 'POST':
        file = request.FILES['pcap_file']

        unique_filename = str(uuid.uuid4()) + '_' + file.name
        file_path = join(settings.MEDIA_ROOT, unique_filename)

        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        request.session['file_path'] = file_path
        return redirect('filter_pcap')

    return render(request, 'upload.html')

def filter_pcap(request):
    file_path = request.session.get('file_path')

    if not file_path:
        return redirect('upload_pcap_file')

    form = PacketFilterForm(request.GET)

    if form.is_valid():
        from_value = form.cleaned_data['from_value']
        to_value = form.cleaned_data['to_value']

        if from_value:
            from_value = from_value.strip().lstrip('+').lower()
        if to_value:
            to_value = to_value.strip().lstrip('+').lower()

        analysis_results = analyze_pcap(file_path, from_value, to_value)

        if 'error' in analysis_results:
            print(analysis_results['error'])
        else:
            packet_details = analysis_results.get('packet_details', [])
            packet_count = analysis_results.get('packet_count', 0)

            if not packet_details:
                analysis_results['error'] = 'No packets matching the filter found.'

    else:
        analysis_results = {'error': 'Invalid form data. Please check your input.'}

        for packet in analysis_results.get('packet_details', []):
          if 'time' in packet and packet['time']:
             timestamp = packet['time']
             print("Timestamp before conversion:", timestamp)  # Ajoutez cette ligne pour le débogage
             converted_time = timezone.make_aware(datetime.fromtimestamp(timestamp), timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
             print("Converted time:", converted_time)  # Ajoutez cette ligne pour le débogage
             packet['time'] = converted_time
 
    # Inclure la valeur de 'time' dans le contexte du modèle
    context = {
        'form': form,
        'packet_count': analysis_results.get('packet_count', 0),
        'packet_details': analysis_results.get('packet_details', []),
        'error': analysis_results.get('error'),
    }

    return render(request, 'filter.html', context)


#FRONTEND

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import AnalysisResult

class AnalysisResultsView(APIView):
    def get(self, request):
        # Obtenez le chemin du fichier pcap depuis la session
        file_path = request.session.get('file_path')
        
        # Vos valeurs de filtrage (ajoutez plus de champs si nécessaire)
        from_value = request.query_params.get('from_value')
        to_value = request.query_params.get('to_value')

        # Utilisez la fonction analyze_pcap pour obtenir les résultats d'analyse
        analysis_results = analyze_pcap(file_path, from_value, to_value)

        if 'error' in analysis_results:
            return Response({'error': analysis_results['error']}, status=status.HTTP_400_BAD_REQUEST)

        # Formattez les résultats d'analyse au format JSON
        data = {
            'packet_count': analysis_results.get('packet_count', 0),
            'packet_details': analysis_results.get('packet_details', []),
        }

        return Response(data, status=status.HTTP_200_OK)
