hooks = {}


class Hook:
    def __init__(self, target, hook_type, source, catch_return):
        self.target = target
        self.hook_type = hook_type
        self.source = source
        self.catch_return = catch_return


def hook(source, target: str, hook_type: int, catch_return: bool = False) -> Hook:
    """
    注入对应的模块，使在执行对应模块的前后执行特定的函数。详细请见插件开发文档。

    :param source: function 要注入的函数
    :param target: str 注入目标路径
    :param hook_type: int 注入方式（0：原函数之前执行，1：原函数之后执行，2：覆盖原函数）
    :param catch_return: bool 是否劫持原函数的返回值。如果劫持，原函数的返回值会以最后一个形参传入，并以注入的函数的返回值作为原函数的返回值
    :return: Hook 返回钩子
    """
    if target not in hooks:
        hooks[target] = {
            'before': [],
            'overwrite': None,
            'after': []
        }
    root = hooks[target]
    content = Hook(target, hook_type, source, catch_return)
    if hook_type == 0:
        root['before'].append(content)
    elif hook_type == 1:
        root['after'].append(content)
    elif hook_type == 2:
        if root['overwrite'] is not None:
            raise RuntimeError('不能对一个已经被覆写过的函数再次覆写。')
        root['overwrite'] = content
    else:
        raise ValueError('未知的注入方式。')
    return content


def unhook(content: Hook):
    """
    将钩子脱钩。

    :param content: Hook 钩子
    :return: None
    """
    try:
        root = hooks[content.target]
        if content.hook_type == 0:
            root['before'].remove(content)
        elif content.hook_type == 1:
            root['after'].remove(content)
        else:
            root['overwrite'] = None
    except ValueError:
        raise ValueError('钩子不存在或者已经脱钩。')


def hook_target(path):
    def wrapper(func):
        def run(*args, **kwargs):
            if path in hooks:
                last_return = None
                root = hooks[path]
                for i in root['before']:  # hooks before
                    if i.catch_return:
                        last_return = i.source(*args, **kwargs, last_return=last_return)
                    else:
                        i.source(*args, **kwargs)

                if root['overwrite'] is None:  # overwrite hook
                    last_return = func(*args, **kwargs)
                else:
                    if root['overwrite'].catch_return:
                        last_return = root['overwrite'].source(*args, **kwargs, last_return=last_return)
                    else:
                        root['overwrite'].source(*args, **kwargs)

                for i in root['after']:  # hooks after
                    if i.catch_return:
                        last_return = i.source(*args, **kwargs, last_return=last_return)
                    else:
                        i.source(*args, **kwargs)
                return last_return
            else:
                return func(*args, **kwargs)

        return run

    return wrapper


class ClassHookMgr:
    def __init__(self):
        self.hooks = {}

    def hook(self, source, target: str, hook_type: int, catch_return: bool = False) -> Hook:
        """
        注入对应的模块，使在执行对应模块的前后执行特定的函数。详细请见插件开发文档。

        :param source: function 要注入的函数
        :param target: str 注入目标路径
        :param hook_type: int 注入方式（0：原函数之前执行，1：原函数之后执行，2：覆盖原函数）
        :param catch_return: bool 是否劫持原函数的返回值。如果劫持，原函数的返回值会以最后一个形参传入，并以注入的函数的返回值作为原函数的返回值
        :return: Hook 返回钩子
        """
        if target not in self.hooks:
            self.hooks[target] = {
                'before': [],
                'overwrite': None,
                'after': []
            }
        root = self.hooks[target]
        content = Hook(target, hook_type, source, catch_return)
        if hook_type == 0:
            root['before'].append(content)
        elif hook_type == 1:
            root['after'].append(content)
        elif hook_type == 2:
            if root['overwrite'] is not None:
                raise RuntimeError('不能对一个已经被覆写过的函数再次覆写。')
            root['overwrite'] = content
        else:
            raise ValueError('未知的注入方式。')
        return content

    def unhook(self, content: Hook):
        """
        将钩子脱钩。

        :param content: Hook 钩子
        :return: None
        """
        try:
            root = self.hooks[content.target]
            if content.hook_type == 0:
                root['before'].remove(content)
            elif content.hook_type == 1:
                root['after'].remove(content)
            else:
                root['overwrite'] = None
        except ValueError:
            raise ValueError('钩子不存在或者已经脱钩。')


def class_hook_target(path):
    def wrapper(func):
        def run(self, *args, **kwargs):
            if path in self.hook_mgr.hooks:
                last_return = None
                root = self.hook_mgr.hooks[path]
                for i in root['before']:  # hooks before
                    if i.catch_return:
                        last_return = i.source(self, *args, **kwargs, last_return=last_return)
                    else:
                        i.source(self, *args, **kwargs)

                if root['overwrite'] is None:  # overwrite hook
                    last_return = func(self, *args, **kwargs)
                else:
                    if root['overwrite'].catch_return:
                        last_return = root['overwrite'].source(self, *args, **kwargs, last_return=last_return)
                    else:
                        root['overwrite'].source(self, *args, **kwargs)

                for i in root['after']:  # hooks after
                    if i.catch_return:
                        last_return = i.source(self, *args, **kwargs, last_return=last_return)
                    else:
                        i.source(self, *args, **kwargs)
                return last_return
            else:
                return func(self, *args, **kwargs)

        return run

    return wrapper
