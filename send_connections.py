import os
import sys
import time
from random import uniform
from time import sleep

from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger.add("logs/logs.log", serialize=False, encoding='utf-8')
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    backtrace=True,
    diagnose=True
)
logger.opt(colors=True)


class BotSendConnectionLinkedin:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.succesful_connections = 0
        self.url = 'https://www.linkedin.com/feed/'

    def initilize_driver(self):
        """Inicializa o driver do chrome"""

        user_data = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--lang=pt-BR")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("window-size=1920x1080")
        chrome_options.add_argument(f"--user-data-dir={user_data}")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(
            self.driver,
            timeout=15,
            poll_frequency=1,
            ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException,
                ElementNotSelectableException,
                ElementNotInteractableException
            ]
        )

        return self.wait, self.driver

    def sleeping(self, start=1.5, end=3.0):
        """Tempo de espera entre as ações, para simular um usuário real, o tempo é aleatório"""
        sleep(uniform(start, end))

    def scroll_to_bottom(self):
        """Desce a página até o final"""
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    @classmethod
    def slow_typing(cls, field, message: str):
        """Escreve a mensagem letra por letra
        :param field: campo que será escrito
        :param message: mensagem que será escrita
        """

        for letter in message:
            sleep(uniform(0.1, 5 / 30))
            field.send_keys(letter)

    def send_connections(self, profession, message):
        """
        Envia conexões para as pessoas que aparecem na pesquisa, filtrando por pessoas.
        Há dois loops, o primeiro é responsavel por verificar se há mais botões de conectar disponíveis, e o segundo
        loop é responsavel por clicar no botão de avançar caso não haja mais botões de conectar na página, o mesmo é
        interrompido quando não há mais botões de avançar.

        :param profession: profissão que será pesquisada
        :param message: mensagem personalizada que será enviada para as pessoas
        """
        logger.info('Entrando no site')
        self.initilize_driver()
        self.driver.get(self.url)
        self.sleeping()

        logger.info(f'Pesquisando por: {profession}')
        search = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@type="text"]')))
        search.click()

        self.slow_typing(search, profession)
        search.send_keys(Keys.ENTER)

        logger.info('Filtrando por pessoas.')
        people_button = self.wait.until(
            EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Pessoas"]')))
        self.sleeping()
        people_button[0].click()

        self.sleeping()
        self.scroll_to_bottom()

        button_next = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//button//span[text()="Avançar"]')))

        self.sleeping(0.6, 1.2)
        self.driver.execute_script('window.scrollTo(0, 0)')

        while True:
            while True:
                try:
                    buttons_connect = self.wait.until(
                        EC.visibility_of_all_elements_located((By.XPATH, '//button//span[text()="Conectar"]')))
                except:
                    buttons_connect = False

                if not buttons_connect:
                    self.scroll_to_bottom()
                    button_next = self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, '//button//span[text()="Avançar"]')))
                    self.driver.execute_script('arguments[0].click()', button_next)
                else:
                    break

                if not button_next:
                    logger.warning('Não há mais botões para avançar')
                    break

            if not button_next:
                logger.warning('Não há mais botões para avançar')
                break

            for button in buttons_connect:
                self.sleeping()
                button.click()
                self.succesful_connections += 1

                if message:
                    button_add_note = self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, '//button[@aria-label="Adicionar nota"]')))
                    self.sleeping()
                    button_add_note.click()

                    text_with_name = self.wait.until(
                        EC.visibility_of_element_located((By.ID, 'send-invite-modal')))

                    text = text_with_name.text.split()
                    name = text[1]

                    if name:
                        personalized_message = f'Olá {name} {message}'
                    else:
                        personalized_message = message

                    field_note = self.wait.until(
                        EC.visibility_of_element_located((By.ID, 'custom-message')))

                    field_note.send_keys(personalized_message)
                    # self.slow_typing(field_note, personalized_message)

                    send_connection = self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, '//button[@aria-label="Enviar agora"]')))
                    self.sleeping()
                    send_connection.click()

                logger.info('Conexão enviada com sucesso, {} conexões enviadas'.format(self.succesful_connections))
                self.sleeping()

        logger.warning('Fim do programa')
        self.driver.quit()
