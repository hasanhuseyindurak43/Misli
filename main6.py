from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class Application():
    def __init__(self):
        self.team_names = self.get_team_names()
        self.driver = self.start_browser()
        self.accept_cookies()
        self.scroll_to_bottom()
        self.html = self.get_html_source()
        self.maclar = self.parse_html()
        self.driver.quit()
        print("Maçlar:", self.maclar)
        self.results = self.play_matches()
        self.print_combined_results()

    def get_team_names(self):
        # Kullanıcıdan kaç takım gireceğini sormak
        num_teams = int(input("Kaç takım gireceksiniz? "))
        # Takım isimlerini saklamak için bir liste oluşturun
        team_names = []
        # Kullanıcıdan takım isimlerini almak için for döngüsü
        for i in range(num_teams):
            team_name = input(f"{i + 1}. takımın ismini girin: ")
            team_names.append(team_name)
        print("Takım isimleri:", team_names)
        return team_names

    def start_browser(self):
        # Tarayıcıyı başlatın
        driver = webdriver.Chrome()
        # Tarayıcı penceresini maksimum boyuta ayarlayın
        driver.maximize_window()
        url = "https://www.misli.com"
        # Belirtilen URL'ye gidin
        driver.get(f'{url}/iddaa/futbol')
        return driver

    def accept_cookies(self):
        try:
            # "onetrust-accept-btn-handler" id'sine sahip butonun görünmesini bekleyin ve tıklayın
            accept_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_button.click()
            print("Clicked the accept button.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def scroll_to_bottom(self):
        # Sayfanın tamamen yüklenmesi için bekleyin
        time.sleep(5)  # Gerekirse bu süreyi ayarlayın
        # Sayfanın en altına kadar 100 piksel kademelerle kaydırma işlemi
        scroll_pause_time = 0.1  # Her kaydırma adımında bekleme süresi
        # Belirli bir sınır belirlemeksizin sayfanın sonuna kadar kaydırma
        for _ in range(100):  # Yeterli sayıda döngü
            self.driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            current_scroll_position = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            if current_scroll_position >= new_height:
                break

    def get_html_source(self):
        # Sayfanın HTML kaynağını alın
        return self.driver.page_source

    def parse_html(self):
        # BeautifulSoup ile HTML kaynağını parse edin
        soup = BeautifulSoup(self.html, 'html.parser')
        # 'bultenpre-futbol' id'sine sahip div'i bulun
        bultenpre_futbol_div = soup.find('div', id='bultenpre-futbol')
        maclar = []

        if bultenpre_futbol_div:
            # 'bulletinRowWrapperPre' classına sahip div'leri bulun
            bulletin_row_wrappers = bultenpre_futbol_div.find_all('div', class_='bulletinRowWrapperPre')
            url = "https://www.misli.com"

            for wrapper in bulletin_row_wrappers:
                # 'bulletinItemInside' classına sahip div'leri bulun
                bulletin_item_insides = wrapper.find_all('div', class_='bulletinItemInside')

                for item_inside in bulletin_item_insides:
                    # 'bulletinItemRow' classına sahip elementleri bulun
                    bulletin_item_rows = item_inside.find_all('div', class_='bulletinItemRow')

                    for item_row in bulletin_item_rows:
                        # 'bulletinTeamName bulletinHomeTeam' classına sahip span'ları bulun
                        home_team = item_row.find('span', class_='bulletinTeamName bulletinHomeTeam')
                        away_team = item_row.find('span', class_='bulletinTeamName bulletinAwayTeam')

                        # 'bulletinOddsWrapper' classına sahip div'leri bulun
                        odds_wrappers = item_row.find_all('div', class_='bulletinOddsWrapper')

                        for odds_wrapper in odds_wrappers:
                            # 'eventDetailMobile' classına sahip 'a' etiketini bulun
                            event_detail_link = odds_wrapper.find('a', class_='eventDetailMobile')
                            if event_detail_link:
                                href = event_detail_link.get('href')

                                # 'oddsCount fs-14 fw-600' classına sahip 'span' etiketini bulun
                                odds_count_span = event_detail_link.find('span', class_='oddsCount fs-14 fw-600')
                                if odds_count_span:
                                    odds_count = odds_count_span.text

                                    # Takım isimleri ile karşılaştırma yapın ve eşleşenleri yazdırın
                                    if home_team and away_team:
                                        if home_team.text in self.team_names or away_team.text in self.team_names:
                                            match_info = {
                                                "home_team": home_team.text,
                                                "away_team": away_team.text,
                                                "href": f"{url}{href}",
                                                "odds_count": odds_count
                                            }
                                            maclar.append(match_info)
                                            print(f"Home Team: {home_team.text}")
                                            print(f"Away Team: {away_team.text}")
                                            print(f"Event Detail Link: {url}{href}")
                                            print(f"Odds Count: {odds_count}")
                                            print("-----")
        else:
            print('Div with id "bultenpre-futbol" not found.')
        return maclar

    def play_matches(self):
        results = []
        for match in self.maclar:
            # Yeni bir tarayıcı başlat
            driver = self.start_browser()

            # Yeni sekme aç
            driver.execute_script("window.open('');")
            # Yeni sekmeye geç
            driver.switch_to.window(driver.window_handles[-1])
            # Href'i aç
            driver.get(match["href"])

            try:
                # Çerezleri kabul et
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "onetrust-consent-sdk"))
                )
                cookie_div = driver.find_element(By.ID, "onetrust-consent-sdk")
                button_group = cookie_div.find_element(By.ID, "onetrust-button-group-parent")
                accept_button = button_group.find_element(By.ID, "onetrust-accept-btn-handler")
                accept_button.click()

                # Sayfanın yüklenmesini bekle
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "marketTabItem")))

                first_half_results = []
                second_half_results = []
                three_half_results = []

                # 'marketTabItem' classına sahip div'i bulun
                market_tabs = driver.find_elements(By.XPATH, "//div[contains(@class, 'marketTabItem taraf')]")

                for tab in market_tabs:
                    # 'marketItem' classına sahip div'in içindeki 'marketTitle' classına sahip p'yi bulun
                    market_items = tab.find_elements(By.CLASS_NAME, "marketItem")

                    for item in market_items:
                        market_title = item.find_element(By.CLASS_NAME, "marketTitle")
                        if "İlk Yarı Sonucu" in market_title.text:
                            # 'marketOddsContainer' classına sahip div'in içindeki 'marketOddsWrapper' div'lerini bulun
                            odds_containers = item.find_elements(By.CLASS_NAME, "marketOddsContainer")

                            for container in odds_containers:
                                odds_wrappers = container.find_elements(By.CLASS_NAME, "marketOddsWrapper")

                                for wrapper in odds_wrappers:
                                    # 'marketOdds' classına sahip div'in içindeki 'oddItem' classına sahip div'leri bulun
                                    odds = wrapper.find_elements(By.CLASS_NAME, "marketOdds")

                                    for odd in odds:
                                        odd_items = odd.find_elements(By.CLASS_NAME, "oddItem")

                                        for odd_item in odd_items:
                                            try:
                                                odd_inside = odd_item.find_element(By.CLASS_NAME, "oddInside")
                                                odd_name = odd_inside.find_element(By.CLASS_NAME, "oddName").text
                                                odd_value_text = odd_inside.find_element(By.CLASS_NAME,
                                                                                         "oddValue").text.replace(",",
                                                                                                                  ".").strip()
                                                odd_value = float(odd_value_text)

                                                if odd_value < 3.00:
                                                    first_half_results.append({
                                                        "home_team": match["home_team"],
                                                        "away_team": match["away_team"],
                                                        "odd_name": odd_name,
                                                        "odd_value": odd_value
                                                    })
                                            except Exception as e:
                                                print(f"An error occurred: {e}")

                        if "İkinci Yarı Sonucu" in market_title.text:
                            # 'marketOddsContainer' classına sahip div'in içindeki 'marketOddsWrapper' div'lerini bulun
                            odds_containers = item.find_elements(By.CLASS_NAME, "marketOddsContainer")

                            for container in odds_containers:
                                odds_wrappers = container.find_elements(By.CLASS_NAME, "marketOddsWrapper")

                                for wrapper in odds_wrappers:
                                    # 'marketOdds' classına sahip div'in içindeki 'oddItem' classına sahip div'leri bulun
                                    odds = wrapper.find_elements(By.CLASS_NAME, "marketOdds")

                                    for odd in odds:
                                        odd_items = odd.find_elements(By.CLASS_NAME, "oddItem")

                                        for odd_item in odd_items:
                                            try:
                                                odd_inside = odd_item.find_element(By.CLASS_NAME, "oddInside")
                                                odd_name = odd_inside.find_element(By.CLASS_NAME, "oddName").text
                                                odd_value_text = odd_inside.find_element(By.CLASS_NAME,
                                                                                         "oddValue").text.replace(",",
                                                                                                                  ".").strip()
                                                odd_value = float(odd_value_text)

                                                if odd_value < 3.00:
                                                    second_half_results.append({
                                                        "home_team": match["home_team"],
                                                        "away_team": match["away_team"],
                                                        "odd_name": odd_name,
                                                        "odd_value": odd_value
                                                    })
                                            except Exception as e:
                                                print(f"An error occurred: {e}")

                        if "İlk Yarı / Maç Sonucu" in market_title.text:
                            # 'marketOddsContainer' classına sahip div'in içindeki 'marketOddsWrapper' div'lerini bulun
                            odds_containers = item.find_elements(By.CLASS_NAME, "marketOddsContainer")

                            for container in odds_containers:
                                odds_wrappers = container.find_elements(By.CLASS_NAME, "marketOddsWrapper")

                                for wrapper in odds_wrappers:
                                    # 'marketOdds' classına sahip div'in içindeki 'oddItem' classına sahip div'leri bulun
                                    odds = wrapper.find_elements(By.CLASS_NAME, "marketOdds")

                                    for odd in odds:
                                        odd_items = odd.find_elements(By.CLASS_NAME, "oddItem")

                                        for odd_item in odd_items:
                                            try:
                                                odd_inside = odd_item.find_element(By.CLASS_NAME, "oddInside")
                                                odd_name = odd_inside.find_element(By.CLASS_NAME, "oddName").text

                                                for first_result in first_half_results:
                                                    for second_result in second_half_results:
                                                        sonuc = f"{first_result['odd_name']}/{second_result['odd_name']}"
                                                        if sonuc == str(odd_name):
                                                            odd_value_text = odd_inside.find_element(By.CLASS_NAME,
                                                                                                     "oddValue").text.replace(
                                                                ",", ".").strip()
                                                            odd_value = float(odd_value_text)

                                                            three_half_results.append({
                                                                "home_team": match["home_team"],
                                                                "away_team": match["away_team"],
                                                                "odd_name": odd_name,
                                                                "odd_value": odd_value
                                                            })
                                            except Exception as e:
                                                print(f"An error occurred: {e}")

                results.append({
                    "home_team": match["home_team"],
                    "away_team": match["away_team"],
                    "first_half_results": first_half_results,
                    "second_half_results": second_half_results,
                    "three_half_results": three_half_results
                })

            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                driver.quit()

        return results

    def print_combined_results(self):
        def combine(matches, current_combination, all_combinations):
            if len(current_combination) == len(matches):
                all_combinations.append(list(current_combination))
                return

            next_match_index = len(current_combination)
            next_match = matches[next_match_index]

            for result in next_match['three_half_results']:
                current_combination.append(result)
                combine(matches, current_combination, all_combinations)
                current_combination.pop()

        combined_results = []
        combine(self.results, [], combined_results)

        # Kombinasyonları yazdırın
        for i, combination in enumerate(combined_results, 1):
            combination_str = " - ".join([
                f"{result['home_team']} - {result['away_team']} : {result['odd_name']} ({result['odd_value']})"
                for result in combination
            ])
            print(f"{i} -) {combination_str}")
            print("-----")

if __name__ == '__main__':
    app = Application()
