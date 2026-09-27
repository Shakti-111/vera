# For member C
golden_test_set = [
    {
        "question": "What is Bluetooth used for?",
        "expected_answer": "Exchanging data between fixed and mobile devices over short distances and building personal area networks (PANs)."
    },
    {
        "question": "What frequency range does Bluetooth use?",
        "expected_answer": "2.402 GHz to 2.48 GHz."
    },
    {
        "question": "What is the maximum range of Bluetooth in its most widely used mode?",
        "expected_answer": "Up to 10 metres (33 ft)."
    },
    {
        "question": "What standard is Wi-Fi based on?",
        "expected_answer": "802.11 standards."
    },
    {
        "question": "What is LoRa short for?",
        "expected_answer": "Long Range."
    },
    {
        "question": "What type of network technology is LoRa used for?",
        "expected_answer": "Non-cellular Low Power Wide Area (LPWA) wireless communication network technology."
    },
    {
        "question": "What is Zigbee based on?",
        "expected_answer": "IEEE 802.15.4-based specification."
    },
    {
        "question": "What is the transmission distance range for Zigbee?",
        "expected_answer": "10–100 meters (33–328 ft)."
    },
    {
        "question": "How does Zigbee transmit data over long distances?",
        "expected_answer": "By passing data through a mesh network of devices."
    },
    {
        "question": "What IEEE standard was used to standardize Bluetooth?",
        "expected_answer": "IEEE 802.15.1."
    },
#     {
#     "question": "What is the maximum battery life of a Bluetooth module?",
#     "expected_answer": "The document specifies a 500-hour battery life for Bluetooth modules."
# },
# {
#     "question": "What are the transmission ranges of Bluetooth and Zigbee?",
#     "expected_answer": "Bluetooth has a range of up to 10 metres, while Zigbee has a longer range of 10-100 metres."
# },
# {
#     "question": "Which communication technology mentioned has the longest possible range?",
#     "expected_answer": "LoRa has the longest range, supporting 2-5km in towns and 10-15km in rural areas."
# },
# {
#     "question": "What do Bluetooth, Wi-Fi, and Zigbee have in common?",
#     "expected_answer": "They are all wireless communication technologies used for connecting IoT devices."
# }
]

if __name__ == "__main__":
    print(f"Golden test set loaded: {len(golden_test_set)} questions")
    for i, item in enumerate(golden_test_set, 1):
        print(f"{i}. {item['question']}")