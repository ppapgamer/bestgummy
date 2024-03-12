# Atlas Inc. Best Gummy
A discord bot that hosts the "Best Gummy" game on discord servers

### Best Gummy
One discord user starts with the "Best Gummy" and gains time as they continue holding it. Another user can steal this role by tagging that user in a specified discord channel. The winner is decided by whoever has the most total held time of the role in a given time period. 

##### Math Gummy
An extension of Best Gummy that forces users to solve a given math problem before obtaining the role.

### Built with
[Texlive](https://www.tug.org/texlive/) - used to generate pretty math questions 

[discord.py](https://discordpy.readthedocs.io/en/stable/) - used to host the discord bot

[dvipng](https://www.nongnu.org/dvipng/) - converts TeX into png format

### Requirements
Uses these python libraries (my requirements.txt):

```
discord.py==2.3.2
Pillow==10.2.0
sympy==1.12
requests==2.31.0
pyyaml==6.0.1
```

Texlive can be installed via `apt install` on Ubuntu
```
apt install texlive-latex-extra -y
```

dviping can be installed via `apt install` on Ubuntu
```
apt install dvipng -y
```
