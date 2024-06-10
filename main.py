import requests, re, dotenv
import pandas as pd, matplotlib.pyplot as plt
from requests import Session

class CrewTracking:
    def __init__(self, base_url):
        self.base_url = base_url
        self.username = dotenv.get_variable('.env', 'USERNAME')
        self.password = dotenv.get_variable('.env', 'PASSWORD')
        self.session = Session()
        self.csrf_token = None
        self.data = None

    def get_csrf_token(self):
        index = self.session.get(f"{self.base_url}/login")
        self.csrf_token = re.search(r'name="_token" type="hidden" value="(.+?)"', index.text).group(1)

    def login(self):
        self.get_csrf_token()
        login = self.session.post(f"{self.base_url}/login", data={
            "_token": self.csrf_token,
            "USERNAME": self.username,
            "PASSWORD": self.password
        })
        if login.status_code != 200:
            raise Exception("Login failed")
        
    def fetch_data(self, endpoint):
        response = self.session.get(f"{self.base_url}{endpoint}")
        self.data = response.json()

    def extract_crewtrainer_counts(self):
        crewtrainer_counts = {}
        for entry in self.data['data']['data']:
            crewtrainer_name = entry['crewtrainer']['name']
            if crewtrainer_name in crewtrainer_counts:
                crewtrainer_counts[crewtrainer_name] += 1
            else:
                crewtrainer_counts[crewtrainer_name] = 1
        return crewtrainer_counts

    def to_dataframe(self, crewtrainer_counts):
        return pd.DataFrame(list(crewtrainer_counts.items()), columns=['Crewtrainer', 'Niet Uitgevoerde Trainingen'])

    def plot_data(self, df):
        df = df.sort_values(by="Niet Uitgevoerde Trainingen", ascending=False)
        plt.figure(figsize=(10, 6))
        plt.barh(df["Crewtrainer"], df["Niet Uitgevoerde Trainingen"], color='skyblue')
        plt.xlabel('Aantal Niet Uitgevoerde Trainingen')
        plt.title('Niet Uitgevoerde Trainingen per Crewtrainer')
        plt.gca().invert_yaxis()  # Highest values at the top
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    base_url = "https://crewtracking.nl/public/index.php"
    endpoint = "/vue/schedule-filled-form/not-entered"

    crew_tracking = CrewTracking(base_url)
    crew_tracking.login()
    crew_tracking.fetch_data(endpoint)
    crewtrainer_counts = crew_tracking.extract_crewtrainer_counts()
    df_crewtrainer = crew_tracking.to_dataframe(crewtrainer_counts)
    crew_tracking.plot_data(df_crewtrainer)
