from threading import Thread

from send_connections import BotSendConnectionLinkedin

if __name__ == '__main__':
    bot_linkedin = BotSendConnectionLinkedin()
    thread_bot_linkedin = Thread(target=bot_linkedin.send_connections, args=(
        'Desenvolvedor Python',
        ',gostaria de conectar com você, pois estou buscando novas conexões para minha rede, muito obrigado!'))
    thread_bot_linkedin.daemon = True

    thread_bot_linkedin.start()
    thread_bot_linkedin.join()


