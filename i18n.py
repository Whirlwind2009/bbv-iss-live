"""i18n.py - English / Hindi text for BBV ISS LIVE.

Every piece of text the visitor reads is here, so a teacher can correct a
sentence without touching the program logic.  Use tr(lang, "key", name=value).
Please have a Hindi teacher review the Hindi text before the event.
"""

LANGS = {"English": "en", "हिन्दी": "hi"}

STRINGS = {
    "en": {
        # header / sidebar
        "title": "BBV ISS LIVE — Mission Control",
        "subtitle": "From Code to Cosmos: how Python turns space data into knowledge.",
        "tagline": "One Planet. One Orbit. Live Data.",
        "school_name": "BIRLA BALIKA VIDYAPEETH, PILANI (Raj.)",
        "school_line1": "A Residential Public School for Girls",
        "school_line2": "A Birla Education Trust Pilani Institution",
        "mode_orbit": "🛰️ Orbit Watch",
        "mode_globe": "🌍 Earth in Motion",
        "mode_lab": "🧪 Space Data Lab",
        "mode_team": "👩‍💻 Meet the Team",
        "display_mode": "Display mode",
        "refresh": "Refresh every (seconds)",
        "force_offline": "Force OFFLINE DEMO (rehearsal)",
        "attract": "Kiosk attract mode (screens change by themselves)",
        "attract_note": "Screens change every {s} seconds.",
        "big_text": "Big text (for large screens)",
        "language": "Language / भाषा",
        "built_with": "Built with Python · Streamlit · Plotly · GitHub",
        "data_src": "Data: {src}",
        # status / metrics
        "st_live": "LIVE",
        "st_delayed": "DELAYED",
        "st_offline": "OFFLINE DEMO",
        "lat": "Latitude",
        "lon": "Longitude",
        "alt": "Altitude",
        "speed": "Speed (km/h)",
        "age": "Data age",
        "age_replay": "n/a (replay)",
        "km_s": "km/s",
        "obs_caption": "Observation time: {utc}  ·  {ist}  ·  Source: {src}",
        "offline_warn": ("**OFFLINE DEMO** – showing a saved *simulated* orbit replay, "
                         "not the real ISS position. {reason} {last}"),
        "reason": "Reason: {err}.",
        "last_real": "Last real reading was {age} ago.",
        "hist_not_writable": "⚠️ History file is not writable here; readings are kept in memory only.",
        "no_data": "No data available - the sample replay file is missing.",
        "prefix_replay": "Replay: ",
        "prefix_none": "",
        "india_in": ("🇮🇳 {prefix}The reported position is inside India's rough bounding box. "
                     "(That is not the same as being directly overhead.)"),
        "india_out": ("🌐 {prefix}The reported position is outside India's rough bounding box. "
                      "Distance from Pilani: about {km} km."),
        "globe_caption": ("The globe turns to keep the station in the centre. The yellow line is the "
                          "recent ground track; the dotted box is a rough outline of India."),
        # map labels
        "lbl_india": "India (rough box)",
        "lbl_track": "Recent ground track",
        "lbl_pilani": "Pilani",
        "lbl_iss": "ISS (latest reported)",
        "lbl_iss_replay": "ISS (replay)",
        "lbl_challenge": "Challenge position",
        # data lab
        "lab_1": "1 · Raw JSON (as received)",
        "lab_no_live": "No live response right now. Replay row shown instead.",
        "lab_2": "2 · After Python validation",
        "lab_checks": ("Checks done: all fields present · numbers valid · latitude/longitude in range · "
                       "altitude and speed plausible · timestamp read and age calculated."),
        "lab_3": "3 · Saved readings",
        "chart_alt": "Altitude over time",
        "chart_speed": "Speed over time",
        "unit_km": "km",
        "units_time": "s|min|h",
        "unit_kmh": "km/h",
        "dl_csv": "⬇️ Download saved readings (CSV)",
        # data detective
        "det_title": "🕵️ Data Detective",
        "det_intro": ("Freeze a reading, read the latitude and longitude, **guess where on Earth** "
                      "the marker will appear - then reveal it."),
        "det_new": "🎯 New challenge",
        "det_needs": "Needs a live reading (not available in offline demo).",
        "det_coords": "Latitude **{lat}°**  ·  Longitude **{lon}°**",
        "det_reveal": "🔍 Reveal on the map",
        "det_dist": "Distance from Pilani: about **{km} km**. Visibility reported: *{vis}*.",
        "det_stale_title": "Live or stale? - how to read the data age",
        "det_stale_body": ("A marker is only 'live' if its **timestamp is recent**. Compare the "
                           "*Observation time* with the clock: under {limit} s is LIVE, older is DELAYED, "
                           "and when the internet fails we show OFFLINE DEMO with a saved simulated replay. "
                           "Always check the age before trusting a value."),
        # orbit counter
        "oc_title": "🌀 Orbit counter",
        "oc_orbits": "Orbits completed",
        "oc_sun": "Sunrises (and sunsets) seen by the crew",
        "oc_time": "Running for",
        "oc_since": "Counting from {when}.",
        "when_screen": "the moment this screen was opened",
        "oc_note": ("Estimate: elapsed time ÷ about {p} min per orbit. "
                    "A simple calculation, not a live measurement."),
        # facts
        "fact_hdr": "💡 Did you know?",
        "fact_note": "Approximate NASA / ISRO facts",
        "facts": [
            "The ISS travels at about 28,000 km/h and circles Earth roughly every 90 minutes.",
            "Astronauts on board see about 16 sunrises and 16 sunsets every day.",
            "The ISS flies about 400 km above Earth's surface.",
            "The ISS is a partnership of five space agencies from many countries.",
            ("Its orbit is tilted 51.6° to the equator, so it never flies beyond about 51.6° north or "
             "south. That is why it can pass near India but never over the poles."),
            ("We can see the ISS only when it reflects sunlight and the sky is dark where we stand - "
             "so it is not visible from Pilani every night."),
            ("The position on this screen is reported by a public API - it is not a radio signal "
             "from the station."),
            "India's Space Vision 2047 includes the planned Bharatiya Antariksh Station by 2035.",
        ],
        # QR and footer
        "qr_title": "Scan to explore on your phone",
        "footer_note": ("Position values are <b>reported data from a public API</b>, not a direct radio "
                        "signal from the station. This exhibit cannot communicate with or control the ISS. "
                        "The ISS is an international partnership; India's planned Bharatiya Antariksh "
                        "Station is a separate Indian programme. No visitor data is collected."),
        # team page
        "team_title": "Meet the Team",
        "team_sub": "The people behind BBV ISS LIVE",
        "team_students": "Student team",
        "team_mentors": "Mentors",
        "class_xi": "Class XI",
        "mentor_role": "Mentor · Computer Science",
        "role_data_t": "Data Team",
        "role_data_d": "Tests the API, reads the JSON, validates fields and records readings.",
        "role_app_t": "Python Application Team",
        "role_app_d": "Writes the functions, handles errors and maintains the dashboard.",
        "role_viz_t": "Visualisation Team",
        "role_viz_d": "Designs the map, charts, labels, colour contrast and display layout.",
        "role_deploy_t": "Deployment & Testing Team",
        "role_deploy_d": "Manages GitHub and Streamlit, tests every device and keeps the offline backup ready.",
        "role_present_t": "Presenter",
        "role_present_d": "Explains the data-to-map journey to visitors in 60–90 seconds.",
    },
    "hi": {
        "title": "BBV ISS LIVE — मिशन कंट्रोल",
        "subtitle": "कोड से ब्रह्मांड तक: पायथन कैसे अंतरिक्ष डेटा को ज्ञान में बदलता है।",
        "tagline": "एक पृथ्वी। एक कक्षा। लाइव डेटा।",
        "school_name": "बिरला बालिका विद्यापीठ, पिलानी (राज.)",
        "school_line1": "बालिकाओं के लिए आवासीय पब्लिक स्कूल",
        "school_line2": "बिरला एजुकेशन ट्रस्ट पिलानी की एक संस्था",
        "mode_orbit": "🛰️ ऑर्बिट वॉच",
        "mode_globe": "🌍 घूमती पृथ्वी",
        "mode_lab": "🧪 स्पेस डेटा लैब",
        "mode_team": "👩‍💻 हमारी टीम",
        "display_mode": "प्रदर्शन मोड",
        "refresh": "रिफ़्रेश अंतराल (सेकंड)",
        "force_offline": "ऑफ़लाइन डेमो चलाएँ (रिहर्सल)",
        "attract": "कियोस्क ऑटो-मोड (स्क्रीन अपने आप बदलें)",
        "attract_note": "हर {s} सेकंड में स्क्रीन बदलती है।",
        "big_text": "बड़े अक्षर (बड़ी स्क्रीन के लिए)",
        "language": "Language / भाषा",
        "built_with": "पायथन · स्ट्रीमलिट · प्लॉटली · गिटहब से निर्मित",
        "data_src": "डेटा स्रोत: {src}",
        "st_live": "लाइव",
        "st_delayed": "विलंबित",
        "st_offline": "ऑफ़लाइन डेमो",
        "lat": "अक्षांश",
        "lon": "देशांतर",
        "alt": "ऊँचाई",
        "speed": "गति (किमी/घंटा)",
        "age": "डेटा की आयु",
        "age_replay": "लागू नहीं (रीप्ले)",
        "km_s": "किमी/से",
        "obs_caption": "अवलोकन का समय: {utc}  ·  {ist}  ·  स्रोत: {src}",
        "offline_warn": ("**ऑफ़लाइन डेमो** – यह सहेजी गई *काल्पनिक (सिम्युलेटेड)* कक्षा का रीप्ले है, "
                         "ISS की वास्तविक स्थिति नहीं। {reason} {last}"),
        "reason": "कारण: {err}.",
        "last_real": "अंतिम वास्तविक रीडिंग {age} पहले की थी।",
        "hist_not_writable": "⚠️ यहाँ हिस्ट्री फ़ाइल में लिखना संभव नहीं; रीडिंग केवल मेमोरी में रखी जा रही हैं।",
        "no_data": "कोई डेटा उपलब्ध नहीं – सैंपल रीप्ले फ़ाइल नहीं मिली।",
        "prefix_replay": "रीप्ले: ",
        "prefix_none": "",
        "india_in": ("🇮🇳 {prefix}रिपोर्ट की गई स्थिति भारत के मोटे आयताकार दायरे के भीतर है। "
                     "(इसका अर्थ ठीक सिर के ऊपर होना नहीं है।)"),
        "india_out": ("🌐 {prefix}रिपोर्ट की गई स्थिति भारत के मोटे आयताकार दायरे के बाहर है। "
                      "पिलानी से दूरी: लगभग {km} किमी।"),
        "globe_caption": ("ग्लोब ISS को केंद्र में रखने के लिए घूमता है। पीली रेखा हाल का ग्राउंड ट्रैक है; "
                          "बिंदीदार डिब्बा भारत की मोटी रूपरेखा है।"),
        "lbl_india": "भारत (मोटा दायरा)",
        "lbl_track": "हाल का ग्राउंड ट्रैक",
        "lbl_pilani": "पिलानी",
        "lbl_iss": "ISS (नवीनतम रिपोर्ट)",
        "lbl_iss_replay": "ISS (रीप्ले)",
        "lbl_challenge": "चुनौती की स्थिति",
        "lab_1": "1 · कच्चा JSON (जैसा मिला)",
        "lab_no_live": "अभी कोई लाइव प्रतिक्रिया नहीं। इसके स्थान पर रीप्ले की पंक्ति दिखाई गई है।",
        "lab_2": "2 · पायथन सत्यापन के बाद",
        "lab_checks": ("की गई जाँचें: सभी फ़ील्ड मौजूद · संख्याएँ मान्य · अक्षांश/देशांतर सीमा में · "
                       "ऊँचाई और गति संभव · टाइमस्टैम्प पढ़कर डेटा की आयु निकाली गई।"),
        "lab_3": "3 · सहेजी गई रीडिंग",
        "chart_alt": "समय के साथ ऊँचाई",
        "chart_speed": "समय के साथ गति",
        "unit_km": "किमी",
        "units_time": "से|मिनट|घं",
        "unit_kmh": "किमी/घंटा",
        "dl_csv": "⬇️ सहेजी गई रीडिंग डाउनलोड करें (CSV)",
        "det_title": "🕵️ डेटा डिटेक्टिव",
        "det_intro": ("एक रीडिंग फ़्रीज़ कीजिए, अक्षांश-देशांतर पढ़िए, **अनुमान लगाइए कि पृथ्वी पर कहाँ** "
                      "मार्कर दिखेगा – फिर नक्शे पर दिखाइए।"),
        "det_new": "🎯 नई चुनौती",
        "det_needs": "इसके लिए लाइव रीडिंग चाहिए (ऑफ़लाइन डेमो में उपलब्ध नहीं)।",
        "det_coords": "अक्षांश **{lat}°**  ·  देशांतर **{lon}°**",
        "det_reveal": "🔍 नक्शे पर दिखाएँ",
        "det_dist": "पिलानी से दूरी: लगभग **{km} किमी**। रिपोर्ट की गई दृश्यता: *{vis}*।",
        "det_stale_title": "लाइव या पुराना? – डेटा की आयु कैसे पढ़ें",
        "det_stale_body": ("मार्कर तभी 'लाइव' है जब उसका **टाइमस्टैम्प हाल का** हो। *अवलोकन का समय* को घड़ी से "
                           "मिलाइए: {limit} सेकंड से कम हो तो लाइव, उससे पुराना हो तो विलंबित, और इंटरनेट बंद होने "
                           "पर हम सहेजे गए काल्पनिक रीप्ले के साथ ऑफ़लाइन डेमो दिखाते हैं। किसी मान पर भरोसा करने "
                           "से पहले उसकी आयु ज़रूर देखें।"),
        "oc_title": "🌀 ऑर्बिट काउंटर",
        "oc_orbits": "पूरी हुई कक्षाएँ",
        "oc_sun": "चालक दल द्वारा देखे गए सूर्योदय (और सूर्यास्त)",
        "oc_time": "चलने का समय",
        "oc_since": "गिनती {when} से।",
        "when_screen": "इस स्क्रीन के खुलने के क्षण",
        "oc_note": ("अनुमान: बीता समय ÷ लगभग {p} मिनट प्रति कक्षा। "
                    "यह साधारण गणना है, लाइव माप नहीं।"),
        "fact_hdr": "💡 क्या आप जानते हैं?",
        "fact_note": "अनुमानित NASA / ISRO तथ्य",
        "facts": [
            "ISS लगभग 28,000 किमी/घंटा की गति से चलता है और लगभग हर 90 मिनट में पृथ्वी का एक चक्कर पूरा करता है।",
            "स्टेशन पर मौजूद अंतरिक्ष यात्री हर दिन लगभग 16 सूर्योदय और 16 सूर्यास्त देखते हैं।",
            "ISS पृथ्वी की सतह से लगभग 400 किमी ऊपर उड़ता है।",
            "ISS अनेक देशों की पाँच अंतरिक्ष एजेंसियों की साझेदारी है।",
            ("इसकी कक्षा भूमध्य रेखा से 51.6° झुकी है, इसलिए यह लगभग 51.6° उत्तर या दक्षिण अक्षांश से आगे "
             "कभी नहीं जाता। इसी कारण यह भारत के पास से गुज़र सकता है, पर ध्रुवों के ऊपर से कभी नहीं।"),
            ("ISS तभी दिखता है जब वह सूर्य का प्रकाश परावर्तित करे और हमारे यहाँ आकाश अँधेरा हो – "
             "इसलिए पिलानी से यह हर रात नहीं दिखता।"),
            "इस स्क्रीन की स्थिति एक सार्वजनिक API से रिपोर्ट की गई है – यह स्टेशन से आया रेडियो संकेत नहीं है।",
            "भारत के अंतरिक्ष विज़न 2047 में 2035 तक प्रस्तावित भारतीय अंतरिक्ष स्टेशन शामिल है।",
        ],
        "qr_title": "फ़ोन पर देखने के लिए स्कैन करें",
        "footer_note": ("दिखाए गए स्थिति-मान <b>सार्वजनिक API द्वारा रिपोर्ट किया गया डेटा</b> हैं, स्टेशन से सीधा "
                        "रेडियो संकेत नहीं। यह प्रदर्शनी ISS से संपर्क या उसे नियंत्रित नहीं कर सकती। ISS एक "
                        "अंतरराष्ट्रीय साझेदारी है; भारत का प्रस्तावित भारतीय अंतरिक्ष स्टेशन एक अलग भारतीय "
                        "कार्यक्रम है। किसी आगंतुक का डेटा एकत्र नहीं किया जाता।"),
        "team_title": "हमारी टीम",
        "team_sub": "BBV ISS LIVE के पीछे की टीम",
        "team_students": "विद्यार्थी टीम",
        "team_mentors": "मार्गदर्शक",
        "class_xi": "कक्षा XI",
        "mentor_role": "मार्गदर्शक · कंप्यूटर साइंस",
        "role_data_t": "डेटा टीम",
        "role_data_d": "API की जाँच, JSON पढ़ना, फ़ील्ड सत्यापित करना और रीडिंग दर्ज करना।",
        "role_app_t": "पायथन एप्लिकेशन टीम",
        "role_app_d": "फ़ंक्शन लिखना, त्रुटियाँ सँभालना और डैशबोर्ड को बनाए रखना।",
        "role_viz_t": "विज़ुअलाइज़ेशन टीम",
        "role_viz_d": "नक्शा, चार्ट, लेबल, रंग-विरोधाभास और डिस्प्ले लेआउट डिज़ाइन करना।",
        "role_deploy_t": "डिप्लॉयमेंट और टेस्टिंग टीम",
        "role_deploy_d": "GitHub और Streamlit सँभालना, हर डिवाइस की जाँच और ऑफ़लाइन बैकअप तैयार रखना।",
        "role_present_t": "प्रस्तुतकर्ता",
        "role_present_d": "आगंतुकों को डेटा से नक्शे तक की यात्रा 60–90 सेकंड में समझाना।",
    },
}


def tr(lang, key, **values):
    """Look up a text in the chosen language (falls back to English)."""
    table = STRINGS.get(lang, STRINGS["en"])
    text = table.get(key)
    if text is None:
        text = STRINGS["en"][key]
    if isinstance(text, str) and values:
        text = text.format(**values)
    return text
