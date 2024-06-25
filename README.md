# SecretSharing

Implementación de un programa en Bash para la compartición de secretos entre 𝑚 personas de tal forma que pueda
recuperarse el secreto si se reúnen, como mínimo, 𝑛 personas, con 𝑛 < 𝑚.

El programa encriptar.py crea 𝑚 ficheros con la clave partida.

El programa desencriptar.py requiere 𝑛 de los 𝑚 ficheros creados para poder recuperar el secreto.
