import pexpect

import logging
logging.basicConfig(level=logging.DEBUG)

from . import helpers


PEXPECT_ERRORS = [pexpect.EOF, pexpect.TIMEOUT]


def validate_login_type(login_type):
    if login_type.lower() not in ['ssh', 'telnet']:
        raise ValueError('Invalid login type {0}. '
                         'Valid types are ssh and telnet'.format(login_type))


def clean_up_error(child, error):
    helpers.debug_output(child)
    child.close()
    helpers.parse_error(error)


def enable_mode(child, enable_password):
    child.sendline('enable')
    a = child.expect(PEXPECT_ERRORS + ['.*assword', '.*#'])
    if a == (0 or 1):
        clean_up_error(child, a)
    elif a == 2:
        if not enable_password:
            child.close()
            raise ValueError('Need enable password, but None provided')
        child.sendline(enable_password)
        b = child.expect(PEXPECT_ERRORS + ['.*#'])
        if b == (0 or 1):
            clean_up_error(child, b)
        elif b == 2:
            return child
    elif a == 3:
        return child


def unix_login(connector, login_type='ssh'):
    """
    Login to linux/unix shell (bash terminal assumed)
    :param connector: Connector object
    :param login_type: SSH or Telnet
    :return: pexpect spawn object

    Authentication types:
     - username and password
     - certificate based
    """
    validate_login_type(login_type)

    login_cmd = connector.ssh_driver if login_type.lower() == 'ssh' else connector.telnet_driver

    child = pexpect.spawn(login_cmd)
    i = child.expect([pexpect.EOF, pexpect.TIMEOUT, '.*#', '.*$', '.*assword.*'])
    if i == (0 or 1):
        raise i
    elif i == (2 or 3):
        return child
    elif i == 4:
        child.sendline(connector.password)
        j = child.expect([pexpect.EOF, pexpect.TIMEOUT, '.*#', '.*$'])
        if j == (0 or 1):
            raise i
        elif j == (2 or 3):
            return child


def cisco_login(connector, login_type='ssh', enable_password=''):
    """
    Login to Cisco IOS, IOS-XE, NXOS
    :param connector: Connector object
    :param login_type: SSH or Telnet
    :param enable_password: Enable password if required
    :return: pexpect spawn object

    Authentication types:
     - username and password
     - certificate based
    """
    validate_login_type(login_type)

    login_cmd = connector.ssh_driver if login_type.lower() == 'ssh' else connector.telnet_driver

    child = pexpect.spawn(login_cmd, timeout=connector.timeout)
    i = child.expect(PEXPECT_ERRORS + ['.*assword', '.*>', '.*#'])
    if i == (0 or 1):
        clean_up_error(child, i)
    elif i == 2:
        child.sendline(connector.password)
        j = child.expect(PEXPECT_ERRORS + ['.*>', '.*#'])
        if j == (0 or 1):
            clean_up_error(child, j)
        elif j == 2:
            return enable_mode(child, enable_password)
        elif j == 3:
            return child
    elif i == 3:
        return enable_mode(child, enable_password)
    elif i == 4:
        return child


def arista_login(connector, login_type='ssh', enable_password=''):
    return cisco_login(connector=connector, login_type=login_type,
                       enable_password=enable_password)


def juniper_login():
    pass
