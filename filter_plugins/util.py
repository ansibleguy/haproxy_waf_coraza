from re import sub as regex_replace


class FilterModule(object):

    def filters(self):
        return {
            'safe_key': self.safe_key,
            'unique_apps': self.unique_apps,
            'is_boolean': self.is_boolean,
        }

    @staticmethod
    def safe_key(key: str) -> str:
        return regex_replace('[^0-9a-zA-Z_]+', '', key.replace(' ', '_'))

    @staticmethod
    def unique_apps(all_apps: list) -> list:
        apps = []

        for app in all_apps:
            try:
                if app['name'] not in apps:
                    apps.append(app)

            except KeyError:
                pass

        return apps

    @staticmethod
    def is_boolean(value: any) -> bool:
        return isinstance(value, bool)
