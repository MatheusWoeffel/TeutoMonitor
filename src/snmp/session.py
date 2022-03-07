from easysnmp import Session


class SNMPSession:
    def __init__(self, host_ip, snmp_version=2, security_username="",
                 privacy_password="", privacy_protocol="",
                 auth_password="", auth_protocol="", community="public"):
        self.host_ip = host_ip
        self.snmp_version = snmp_version
        self.security_username = security_username
        self.privacy_password = privacy_password
        self.privacy_protocol = privacy_protocol
        self.auth_password = auth_password
        self.auth_protocol = auth_protocol

        if self.snmp_version == 2:
            self._session = Session(
                hostname=host_ip, community=community, version=snmp_version)
        elif self.snmp_version == 3:
            self._session = Session(
                hostname=host_ip, version=snmp_version, security_level="auth_with_privacy",
                security_username=security_username, privacy_password=privacy_password,
                privacy_protocol=privacy_protocol, auth_password=auth_password,
                auth_protocol=auth_protocol)
        else:
            self._session = None

    def session(self):
        return self._session

    def get_instance_name(self):
        return self.session().get('sysName.0').value

    def get_interfaces_count(self):
        return int(self.session().get('ifNumber.0').value)
