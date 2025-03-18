# filmweb-backup

Backup your account information from the `filmweb.pl` website.

## TL;DR

Clone the repo:
```
▶ git clone --depth=1 https://github.com/kdybicz/filmweb-backup.git
```

Setup environment:
```
▶ make clean setup
```

To run the backup script:
```
▶ pipenv run python cli.py -t <_artuser_prm cookie>
```

### Cookie

The JWT tokens used by `filmweb.pl` is fairly short-lived, so to make the backup to work, especially for accounts with a bigger amount of rated movies, we need to use a "session cookie" that works like a refresh token. That way, if one JWT token expires new one will be requested. The cookie that holds this "session" is called `_artuser_prm`.

You can find it using Chrome inspector:

![Chrome inspector](https://github.com/kdybicz/filmweb-backup/blob/master/docs/img/cookie.png?raw=true)
