# Relatório MicroPython - ESP32

## Objetivos

* __Objetivo Geral__
Este relatório tem como objetivo fornecer um tutorial detalhado sobre o processo de instalação do firmware MicroPython no microcontrolador ESP32. O intuito é guiar os usuários desde a preparação do ambiente até a execução do primeiro script em MicroPython, garantindo que todas as etapas sejam compreendidas e executadas corretamente.

* __Objetivos Específicos__
Descrever os pré-requisitos necessários para a instalação do MicroPython no ESP32.
Instruir sobre a instalação do Python e das bibliotecas necessárias.
Orientar sobre a instalação do Visual Studio Code e as extensões necessárias.
Demonstrar como realizar as conexões físicas e eletrônicas do ESP32.
Explicar o processo de flashar o firmware MicroPython no ESP32.
Fornecer um exemplo de teste simples, como o "Hello World", para garantir que a instalação foi bem-sucedida.


## Pré-Requisitos

* [Adapter ESP32 Wroom](https://pt.aliexpress.com/item/32980686343.html)
* Dispositivo cujo objetivo é realizar o flashing do firmware MicroPython no ESP32.

* [ESP32 Chip](https://pt.aliexpress.com/item/1005006688246511.html?src=google&src=google&albch=shopping&acnt=768-202-3196&slnk=&plac=&mtctp=&albbt=Google_7_shopping&gclsrc=aw.ds&albagn=888888&isSmbAutoCall=false&needSmbHouyi=false&src=google&albch=shopping&acnt=768-202-3196&slnk=&plac=&mtctp=&albbt=Google_7_shopping&gclsrc=aw.ds&albagn=888888&ds_e_adid=&ds_e_matchtype=&ds_e_device=c&ds_e_network=x&ds_e_product_group_id=&ds_e_product_id=pt1005006688246511&ds_e_product_merchant_id=5336167937&ds_e_product_country=BR&ds_e_product_language=pt&ds_e_product_channel=online&ds_e_product_store_id=&ds_url_v=2&albcp=19639392923&albag=&isSmbAutoCall=false&needSmbHouyi=false&gad_source=1&gclid=Cj0KCQjw97SzBhDaARIsAFHXUWCPQGzFIu05aFicpHMq-HNVHrRtfiHiYfTdaZ4svSn4_VRK593ZEAoaAp6eEALw_wcB&aff_fcid=62323943bd49426fb492e73e581afcf2-1718474516579-05109-UneMJZVf&aff_fsk=UneMJZVf&aff_platform=aaf&sk=UneMJZVf&aff_trace_key=62323943bd49426fb492e73e581afcf2-1718474516579-05109-UneMJZVf&terminal_id=6ad538482beb48c380bd74ad783f221b&afSmartRedirect=y)
* Chip ESP32 que receberá o firmware MicroPython.

* [Python](https://www.python.org/downloads/)
* Nesse tutorial foi usado o Python 3.10.4.

* [Visual Studio Code](https://code.visualstudio.com/download)
* Local será feito todo o processo de instalação.

* __Cabo Micro Usb__

# Instalação

## Libs Necessárias

``` python
pip install esptool
pip install adafruit-ampy
pip install mpy-cross
```
[EspTool](https://github.com/espressif/esptool)

[adafruit-ampy](https://pypi.org/project/adafruit-ampy/)

[mpy-cross](https://github.com/micropython/micropython/tree/master/mpy-cross)

## Extensões Necessárias

[VSCode Serial Monitor](https://github.com/microsoft/vscode-serial-monitor)

[Python](https://github.com/microsoft/pylance-release)

# Aplicação

## Conexões

1. __Coloque o chip no espaço reservado__
![](https://raw.githubusercontent.com/PedroLucasMendes/Project_EchoLogger_PIBIC/main/Figures/WhatsApp%20Image%202024-06-15%20at%2014.35.16.jpeg)

2. __Coloque o cabo micro Usb__
![](https://raw.githubusercontent.com/PedroLucasMendes/Project_EchoLogger_PIBIC/main/Figures/WhatsApp%20Image%202024-06-15%20at%2014.35.15.jpeg)

3. __Ligue o cabo no PC__

## Flashando o MicroPython

1. Faça o download do [MicroPython](https://micropython.org/download/ESP32_GENERIC/) (O usado nesse tutorial foi a versão V1.23.0 .bin)
2. Identifique a porta serial do seu módulo serial (Exemplo usando Windows - COM6 ou COM5).
3. Mantendo pressionado Prog, pressione e solte o RST botão.
4. Abra o Terminal 
5. Execute o seguinte comando.

> python -m esptool --chip esp32 --port COMX erase_flash

6. Depois disso, reinicie seu dispositivo, execute as etapas 3 e 5:
7. Depois execute o seguinte comando.

> python -m esptool --chip esp32 --port COMX --baud 460800 write_flash -z 0x1000 ./Micropython/ESP32_GENERIC-20231005-v1.21.0.bin

__Observações__
* Sempre mantenha o Botão Prog pressionado só solte quando terminar o ultimo passo.

# Testes

## Hello World

1. No proprio terminal possui a aba Serial Monitor clique nele
2. Selecione a porta para fazer a verificação COMX
3. Inicie o monitoramento
4. Selecione a opção toggle terminal mode
5. Escreva o seguinte comando.
> print("hello world!")
6. Isso fará printar na tela o hello world!