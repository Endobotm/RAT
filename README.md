# RAT

## Warning (aka why you shouldn't be here)

If you're reading this, congrats — you've found something you absolutely shouldn't be looking at.  
Pick one:

- [ ] You clicked on a link sent by me or one of your friends and found this → welcome, actually normal.
- [ ] You found this by Googling shady shit → red flag. Leave.
- [ ] You came here to learn how to be malicious → stop, re-evaluate your life choices, and maybe learn Go instead. If you still wanna learn, go to someone who knows what they are going twin, ts made from Stack Overflow and copious amounts of coffee

## For the curious (or cursed)

- If you expected a tutorial on how to ruin someone's day: wrong repo, champ.
- If you expected sympathy: tough luck, go cry into your ISP bill.
- If you expected mercy: what?

---

## About

Anyways this is a project by me, your local dumbass, and I am trying to make a version of my previous RAT but without using discord. So it will have 2 programs, and maybe a bit more functionality.

<details><summary>Spoiler Alert</summary>It had way more than 2 files
</details>

## Features

- Key Logger
- Client IPv4 and IPv6
- Remote CMD
- File Uploading and Downloading to/from Client
- FLASHBANG! the Client
- Message Client
- Client Screen View

## New, to-be, Implemented Features

I definitely did not forget about this project for a few months...Anyways I got the opportunity to test it on an actual external PC outside my network to simulate a real-world use case. It was absolutely fucking horribe so I decided to rewrite the entire socket system. I will also being adding these features to the RAT

- Paranoia
- Detailed Client Info Fetch
- Redirect
- Bluescreen
- PermaClient
- BetterPopUps (Server Side - UI)
- True Logging (Server Side - Utility)

### New Screen View Features (aka "my internet sucks" edition)

I have come to find out most people have genuine authentic ass WiFi so I need to optimize this connection more and more so that the program is actually usable by humans

- Chunked Sending (2000-byte slices, because idk i heard it reduces the load on your wifi and packet loss, its fucking TCP-)
- Better Frame Headers (include the order so things don’t arrive like your marriage)
- Connectivity Analysis (server checks your potato WiFi before streaming)
- Pre-Buffering (tiny buffer to keep things _kinda_ smooth)
- Latency Display (so you can cry while watching 500ms delay in real time, get better internet twin 🥀💔✌️)
- Adaptive Buffer
- Frame Dropping (skips old frames, shows latest one → less slideshow, more “show”... i see myself out)
- Optional Compression (light squeeze, won’t destroy text this time...hopefully)
- Weak Connection Handling:
  - Warn at 5s/15s buffer delay
  - at 25s/35s the server will actively mock your WiFi and ask you to invest your money into your internet instead of fictional internet women
  - At 1 min delay → client yells at server that internet is trash and kills the stream
