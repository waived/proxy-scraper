import sys, os, requests, threading, socket

_active = 0
_proxies = []

def _scrape():
    _api = ''
    if sys.argv[1].lower() == 'http':
        _api ='https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=no&anonymity=all'
    elif sys.argv[1].lower() == 'https':
        _api ='https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=yes&anonymity=all'
    elif sys.argv[1].lower() == 'socks4':
        _api ='https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=1000&country=all&anonymity=all'

    req = requests.get(_api)
    
    if str(req.status_code) == '200':
        global _proxies
        _content = req.content.decode().splitlines()
        for line in _content:
            _proxies.append(line)
    else:
        sys.exit('\033[33mAPI removed/unavailable! Exiting...')
        
def _check(prox):
    global _active, _proxies
    _active +=1
    try:
        _ip, _port = prox.strip().split(":")
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((_ip, int(_port)))
        s.send('GET / HTTP/1.1\r\nHost:www.example.com\r\n\r\n'.encode())
        s.close()
    
        print('\033[32mProxy alive @ ' + _ip + ':' + _port)
    except:
        print('\033[31mProxy dead/unresponsive @ ' + _ip + ':' + _port)
        _proxies.remove(prox)

    _active -=1

def main():
    os.system('clear')
    if len(sys.argv) != 4:
        sys.exit('Usage: <proxy type: http/https/socks4> <# of threads> <output.txt>\r\n')
        
    if not (sys.argv[1].lower() == 'http' or sys.argv[1].lower() == 'https' or sys.argv[1].lower() == 'socks4'):
        sys.exit('Invalid proxy type! Exiting...\r\n')
    
    print('''\033[1m\033[37m
   ___                     ____                         
  / _ \_______ __ ____ __ / __/__________ ____  ___ ____
 / ___/ __/ _ \\\ \ / // /_\ \/ __/ __/ _ `/ _ \/ -_) __/
/_/  /_/  \___/_\_\\_,  //___/\__/_/  \_,_/ .__/\__/_/   
                  /___/                 /_/         
''')
    
    print('Scraping from API...')
    _scrape()
    
    global _proxies, _active
    print('Total of ' + str(len(_proxies)) + ' scraped. Now checking...\r\n')

    for prox in _proxies:
        try:            
            while True:
                if _active != int(sys.argv[2]):
                    x = threading.Thread(target=_check, args=(prox,))
                    x.daemonized = True
                    x.start()
                    break
        except Exception as e:
            print(e)

    # wait till remaining thread/s exit
    while _active != 0:
        pass
    
    print('\033[37m\r\nDone! Flushing alive-proxies to output file...')
    with open(sys.argv[3], 'w') as fwrite:
        for item in _proxies:
            # add line-feed
            fwrite.write(item + '\n')
        fwrite.close()

    sys.exit('Operation complete! Exiting...')

if __name__ == '__main__':
    main()
