### Encrypter:

#### Url: 

[https://trianguloy.github.io/githubPages/Encrypter/encrypter.html](https://trianguloy.github.io/githubPages/Encrypter/encrypter.html)

#### Description:

Encrypts any html using the AES cypher. It was created to encrypt blogger posts for a friend, but can be used with any html, or even text. The generator generates a ready-to-use html that will ask for a password, and when entered correctly it will be replaced with the encrypted html.

Uses the CryptoJS library: https://cryptojs.gitbook.io/docs/

Note: the text is encrypted using the password itself, and the MD5 of the original text is also present to check for decryption validity. I'm unaware of security issues this may have (other than brute force or whatever the CryptoJS library has, if any) so I can not guarantee a perfect encryption. Still it should be more than enough for casual users that check source code.
