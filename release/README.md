# Daymark release builds

These builds open the hosted app at <https://wickeddaymark.onrender.com/>. They need an internet connection and use their own app/browser cookies for sign-in.

## Build an Android APK

Run `./release/build-apk.ps1` from the repository root on a computer with JDK 17, Android SDK Platform 35, and Gradle 8.9 installed. The installable debug APK is written to `release/Daymark.apk`.

## Build a Windows EXE

Run `./release/build-exe.ps1` from the repository root on Windows with Python 3.13 and Microsoft Edge WebView2 Runtime installed. The app is written to `release/Daymark.exe`.

## Build in GitHub Actions

Open the repository's **Actions > Build Daymark release**, choose `apk`, `exe`, or `both`, then run the workflow. Download the resulting `Daymark-...` artifact to get the requested file.

The Android APK is a sideloadable debug build. It is not signed for Play Store publishing. The Windows EXE is unsigned, so Windows may show its normal first-run publisher warning.
