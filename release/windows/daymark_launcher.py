import webview


APP_URL = "https://wickeddaymark.onrender.com/"


if __name__ == "__main__":
    window = webview.create_window(
        "Daymark",
        APP_URL,
        width=1180,
        height=780,
        min_size=(360, 560),
        text_select=True,
    )
    webview.start(debug=False)
