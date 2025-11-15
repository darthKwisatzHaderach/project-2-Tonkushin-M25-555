"""Декораторы для улучшения функциональности базы данных."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
    """
    Декоратор для централизованной обработки ошибок базы данных.
    
    Перехватывает типичные исключения и выводит понятные сообщения об ошибках.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(
                f"Ошибка: Файл данных не найден. "
                f"Возможно, база данных не инициализирована. ({e})"
            )
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """
    Декоратор-фабрика для запроса подтверждения опасных операций.
    
    Args:
        action_name: Название действия для отображения в запросе подтверждения
        
    Returns:
        Декоратор, который запрашивает подтверждение перед выполнением функции
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                response = input(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            except (UnicodeDecodeError, EOFError, KeyboardInterrupt):
                print(f"\n{action_name.capitalize()} отменено.")
                return None
            
            # Очищаем ответ от пробелов и непечатных символов
            # Удаляем все пробельные символы и непечатные символы
            cleaned_response = ''.join(
                c for c in response.strip().lower() if c.isprintable()
            )
            if cleaned_response not in ('y', 'yes', 'да'):
                print(f"{action_name.capitalize()} отменено.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.
    
    Выводит время выполнения в консоль в формате:
    "Функция <имя_функции> выполнилась за X.XXX секунд"
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed_time:.3f} секунд")
        return result
    return wrapper


def create_cacher() -> Callable:
    """
    Создает функцию кэширования с замыканием.
    
    Returns:
        Функция cache_result(key, value_func), которая кэширует результаты вызовов
    """
    cache: dict[str, Any] = {}
    
    def cache_result(key: str, value_func: Callable) -> Any:
        """
        Кэширует результат вызова функции.
        
        Args:
            key: Ключ для кэширования
            value_func: Функция для получения значения, если оно не закэшировано
            
        Returns:
            Закэшированное или вычисленное значение
        """
        if key in cache:
            print(f"[CACHE HIT] Возвращаем закэшированный результат для ключа: {key}")
            return cache[key]
        
        print(f"[CACHE MISS] Вычисляем результат для ключа: {key}")
        result = value_func()
        cache[key] = result
        return result
    
    def clear_cache() -> None:
        """Очищает кэш."""
        cache.clear()
        print("[CACHE] Кэш очищен")
    
    # Добавляем метод очистки кэша
    cache_result.clear = clear_cache  # type: ignore
    
    return cache_result

