# RAT

![Made with Coffee](https://img.shields.io/badge/Made%20with-Coffee%20%26%20Stack%20Overflow-brown?style=flat)
![Status](https://img.shields.io/badge/Status-Rewriting%20Again%20%3E:P-informational?style=flat&color=orange)
![Legality](https://img.shields.io/badge/Legality-Questionable-orange?style=flat)

```
██████╗ ███████╗████████╗████████╗███████╗██████╗     ██████╗  █████╗ ████████╗
██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗╚══██╔══╝
██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝    ██████╔╝███████║   ██║
██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗    ██╔══██╗██╔══██║   ██║
██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║    ██║  ██║██║  ██║   ██║
╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
```

---

## Warning (aka why you shouldn't be here)

If you're reading this, congrats — you've found something you absolutely shouldn't be looking at.  
Pick one:

- [x] You clicked on a link sent by me or one of your friends and found this → welcome, actually normal.
- [ ] You found this by Googling shady shit → red flag. Leave.
- [ ] You came here to learn how to be malicious → stop, re-evaluate your life choices, and maybe learn Go instead. If you still wanna learn, go to someone who knows what they are going twin, ts made from Stack Overflow and copious amounts of coffee

---

## For the curious (or cursed)

- If you expected a tutorial on how to ruin someone's day: **not a tutorial :P**
- If you expected sympathy: **huh?**
- If you expected mercy: **...what?**

---

## About

Anyways this is a project by me, your local dumbass, and I am trying to make a version of my previous RAT but without using discord. So it will have like 2 files, and maybe a bit more functionality.

<details><summary><code><=[(•)]=></code></summary><code>It had way more than 2 files and functionality</code>
</details>

---

## Features

| Feature       | Description                          |
| ------------- | ------------------------------------ |
| Key Logger    | Captures keystrokes                  |
| Network Info  | Client IPv4 and IPv6                 |
| Remote CMD    | Execute commands remotely            |
| File Transfer | Upload/Download files to/from client |
| FLASHBANG!    | Flashbang the Client                 |
| Messaging     | Send messages to client              |
| Screen View   | Real-time(meh) screen viewing        |

---

## New, to-be, Implemented Features

I definitely did not forget about this project for a few months...Anyways I got the opportunity to test it on an actual external PC outside my network to simulate a real-world use case. It was absolutely fucking horribe so I decided to rewrite the entire socket system. I will also being adding these features to the RAT

```diff
+ Paranoia                             <- [TESTING PHASE]
+ Detailed Client Info Fetch           <- [TESTING PHASE]
- Redirect
- Bluescreen
- PermaClient
- BetterPopUps (Server Side - UI)
- True Logging (Server Side - Utility)
```

### ~~New Screen View Features (aka "my internet sucks" edition)~~

```diff
- Removed since...SocketIO :P
```

<pre><del>I have come to find out most people have genuine authentic ass WiFi so I need to optimize this connection more and more so that the program is actually usable by humans

Features:
  Chunked Sending (20000-byte slices, because idk i heard it reduces the load on your wifi and packet loss, its fucking TCP-)
  Better Frame Headers (include the order so things don't arrive like your marriage)
  Connectivity Analysis (server checks your potato WiFi before streaming)
  Pre-Buffering (tiny buffer to keep things _kinda_ smooth)
  Latency Display (so you can cry while watching 60s delay in real time, get better internet twin 🥀💔✌️)
  Adaptive Buffer
  
Weak Connection Handling:
  • Warn at 5s/15s buffer delay
  • at 25s/35s the server will actively mock your WiFi and ask you to invest your money into your internet instead of fictional internet women
  • At 1 min delay → client yells at server that internet is trash and kills the stream</del></pre>

---

## Troll Features lmao

| Command                  | Effect                                                |
| ------------------------ | ----------------------------------------------------- |
| `Australia`              | inverts mouse/screen controls                         |
| `Elevator Music`         | plays hold music through speakers at random intervals |
| `Windows XP`             | changes all system sounds to Windows XP               |
| `Kettle`                 | plays tea kettle whistle building in intensity        |
| `Existential Crisis`     | opens notepad, slowly types philosophical questions   |
| `Typing Monkey`          | randomly types gibberish in active window             |
| `Mouse Ghost`            | cursor moves slightly on its own (gaslighting)        |
| `Desktop Icons Scramble` | rearranges desktop icons randomly                     |
| `Taskbar Hide`           | hides taskbar, reappears 30 seconds later             |
| `Capslock Toggle`        | randomly enables/disables caps while typing           |
| `Sloth`                  | cursor moves at half speed                            |
| `DVD Screensaver`        | spawns bouncing DVD logo window                       |
| `Dial Up`                | plays dial-up internet sounds                         |
| `Error Spam`             | spawns 50 fake error windows                          |
| `Compliment`             | wholesome compliment to screen                        |
| `Insult`                 | creative insult                                       |
| `Fortune Cookie`         | random fortune                                        |
| `Horoscope`              | fake horoscope                                        |
| `Motivational Quote`     | random quote to screen                                |
| `Gnome-d`                | changes desktop to garden gnome                       |

---

<div align="center">

```
Made with spite, coffee, and poor life choices
```

</div>
