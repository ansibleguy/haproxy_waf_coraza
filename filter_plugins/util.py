from re import sub as regex_replace


class FilterModule(object):

    def filters(self):
        return {
            'safe_key': self.safe_key,
            'unique_apps': self.unique_apps,
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
