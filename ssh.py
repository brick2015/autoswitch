import logging
import pexpect

logger = logging.getLogger(__name__)


class SwitcherInnerError(Exception):
    def __str__(self):
        return "switcher inner error: " + " ".join(self.args)


class Ssh(object):

    ERROR = 'Error'
    PROMPT = r'<\S+\>'
    SPROMPT = r'\[\S+\]'
    MORE = '---- More ----'

    def __init__(self, host, user, password, timeout=15):
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.ssh = None

    def login(self):
        error = None
        ssh1_line = 'ssh -1 -o StrictHostKeyChecking=no %s@%s'
        ssh2_line = 'ssh -2 -o StrictHostKeyChecking=no %s@%s'
        for ssh_line in [ssh1_line, ssh2_line]:
            try:
                self.ssh = pexpect.spawn(ssh_line % (self.user, self.host),
                    timeout=self.timeout)
                self.ssh.logfile = open(self.host, 'ab')
                self.ssh.expect('[pP]assword')
                self.ssh.sendline(self.password)
                self.ssh.expect(self.PROMPT)
                logger.info('login to %s success' % self.host)
                _, error = self.send_command('system-view')
                if not error:
                    break
            except pexpect.ExceptionPexpect as e:
                error = e
        if error:
            self.ssh = None
            logger.error('login {0} failed {1}'.format(self.host, e))
            raise e

    def send_command(self, com):
        """ return (str, error)
        """
        self.ssh.sendline(com)
        logger.debug(com)
        ret = []
        error = None
        while True:
            try:
                index = self.ssh.expect([self.ERROR, self.MORE, self.SPROMPT])
                ret.append(self.ssh.before)
                if index == 0:
                    logger.debug('execute "%s" return error' % (com))
                    self.ssh.expect([self.SPROMPT, self.PROMPT])
                    return "".join(ret+[self.ERROR]), SwitcherInnerError(com)
                elif index == 1:
                    self.ssh.send(" ")
                else:
                    return "".join(ret), error
            except (pexpect.TIMEOUT, pexpect.EOF) as e:
                logger.error('execute "%s" failed: %s' % (com, e))
                ret.append(self.ssh.before)
                return "".join(ret), e

    def run(self, cmd, raise_exception=False):
        ret, error = self.send_command(cmd)
        if raise_exception and error:
            raise error
        else:
            return ret

    def save_config(self):
        try:
            while True:
                self.ssh.sendline("quit")
                index = self.expect([self.PROMPT, self.SPROMPT])
                if index == 0:
                    break
            self.ssh.sendline("save")
            index = self.expect("Y/N")
            self.ssh.sendline("Y")
        except:
            pass

    def isalive(self):
        return self.ssh and self.ssh.isalive()

    def terminate(self):
        if self.isalive():
            self.save_config()
            self.ssh.terminate()

    def __enter__(self):
        if not self.isalive():
            self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ssh = Ssh('10.188.0.6', 'backup', 'www.51idc.com')
    with ssh:
        print ssh.run("display cur", raise_exception=True)
