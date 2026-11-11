# Подключение домена hice.agency к сайту

Сайт работает как Cloudflare Worker **website** (сейчас website.4wrd-90.workers.dev). Домен куплен на Porkbun. План: передать DNS домена в Cloudflare и привязать домен к воркеру. Всё делается в браузере, минут за 10 плюс ожидание.

## Шаг 1. Добавить домен в Cloudflare

1. Откройте https://dash.cloudflare.com и войдите в аккаунт, где живёт воркер `website`.
2. Слева **Account Home** → кнопка **Onboard a domain** (или **+ Add** → **Connect a domain**).
3. Введите `hice.agency`, выберите **Quick scan for DNS records** → **Continue**.
4. Тариф: **Free** → **Continue**.
5. Cloudflare покажет найденные DNS-записи. Если там есть записи Porkbun-парковки (A/ALIAS на `pixie.porkbun.com` или IP Porkbun для `hice.agency` и `www`), **удалите их**, иначе привязка к воркеру выдаст ошибку. Почтовые записи (MX, TXT со `spf`), если вы настраивали почту, оставьте. → **Continue to activation**.
6. Cloudflare покажет **два nameserver'а** вида `xxx.ns.cloudflare.com` и `yyy.ns.cloudflare.com`. Скопируйте их, вкладку не закрывайте.

## Шаг 2. Сменить nameservers на Porkbun

1. Откройте https://porkbun.com/account/domainsSpeedy и войдите.
2. Найдите строку `hice.agency`, наведите на неё и нажмите **Details** (или раскройте строку).
3. В пункте **Authoritative Nameservers** нажмите **Edit**.
4. Удалите все строки (`curitiba.ns.porkbun.com` и т.п.) и вставьте два сервера Cloudflare из шага 1.6, каждый на своей строке.
5. **Submit**.
6. Там же проверьте, что **DNSSEC** выключен (если включён, отключите), иначе домен не заработает после смены серверов.

## Шаг 3. Дождаться активации

1. Вернитесь в Cloudflare и нажмите **Check nameservers now**.
2. Обычно домен становится **Active** за 5–60 минут (иногда до 24 часов). Cloudflare пришлёт письмо.

## Шаг 4. Привязать домен к воркеру

1. В Cloudflare: **Workers & Pages** → воркер **website**.
2. Вкладка **Settings** → блок **Domains & Routes** → **+ Add** → **Custom domain**.
3. Введите `hice.agency` → **Add domain**.
4. Повторите **+ Add** → **Custom domain** для `www.hice.agency`.
5. Cloudflare сам создаст DNS-записи и SSL-сертификат. Через несколько минут статус станет **Active**.

Если на шаге 3 вылезла ошибка «a DNS record already exists», зайдите в домен `hice.agency` → **DNS** → **Records**, удалите записи `A`/`AAAA`/`CNAME` для `hice.agency` и `www` и повторите.

## Шаг 5 (по желанию). www → без www

Чтобы `www.hice.agency` перенаправлял на `hice.agency`, вместо пункта 4.4:
1. Домен `hice.agency` → **DNS** → **Records** → **Add record**: тип `A`, имя `www`, IPv4 `192.0.2.1`, Proxy **включён** (оранжевое облако).
2. **Rules** → **Redirect Rules** → **Create rule** → шаблон **Redirect from WWW to root** → **Deploy**.

## Проверка

Откройте https://hice.agency — должен открыться сайт. `website.4wrd-90.workers.dev` продолжит работать параллельно; при желании его можно выключить в **Settings → Domains & Routes** (переключатель workers.dev).
