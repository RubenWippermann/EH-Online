#!/usr/bin/env python3
"""19.10. Top-15 Welle 2b (Online): je ein eigener Abschnitt (Online-/bundesweit-Winkel) auf 10 Seiten.
Idempotent (Marker id="top15-2b"), gezielt, kein Komplettbau. Im Repo-Root: python3 tools/top15-eho-19-10.py
Fachaussagen nur aus: DGUV Grundsatz 304-002 / 304-003 (April 2022), § 19 FeV, DGUV Fachbereich Erste Hilfe (FAQ)."""
import re, json

D3 = '<a href="https://publikationen.dguv.de/regelwerk/dguv-grundsaetze/4432/" rel="noopener" target="_blank">DGUV Grundsatz 304-003</a>'
D2 = '<a href="https://publikationen.dguv.de/regelwerk/dguv-grundsaetze/89/" rel="noopener" target="_blank">DGUV Grundsatz 304-002</a>'
FEV = '<a href="https://www.gesetze-im-internet.de/fev_2010/__19.html" rel="noopener" target="_blank">§ 19 FeV</a>'
FAQ = '<a href="https://www.dguv.de/fb-erstehilfe/faq/index.jsp" rel="noopener" target="_blank">DGUV Fachbereich Erste Hilfe, FAQ</a>'

# slug: (h2, [Absaetze], Quellenzeile)
T = {
 'kurse/lehrkraefte-fortbildung': ('Lehrkräfte-Fortbildung planen: Termin, Frist, Anreise', [
  'Die Lehrkräfte-Fortbildung ist ein Präsenzkurs; den Ort nennt jeder Termin weiter oben. Wer nicht in der Nähe wohnt, vergleicht daher mehrere Termine und plant Anreise und Übernachtung gleich mit.',
  'Wichtiger als der Ort ist die Frist: Die Fortbildung umfasst mindestens 16 Unterrichtseinheiten zu 45 Minuten, je acht medizinisch-fachlich und pädagogisch. Sie verlängert die Lehrberechtigung aber nur, wenn diese noch gültig ist. Ist sie abgelaufen, ist grundsätzlich wieder eine Grundqualifikation entsprechend Themenbereich II mit mindestens 32 Unterrichtseinheiten nötig.',
  'Sieh also zuerst in deine Unterlagen, bis wann deine Lehrberechtigung läuft, und buche rechtzeitig. Ausgebuchte Termine haben eine Warteliste. Sollen mehrere Lehrkräfte gemeinsam fortgebildet werden, kannst du über „Als Kurs vor Ort anfragen“ einen eigenen Termin erfragen.'],
  'Quelle: %s (April 2022), Abschnitt 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D3),
 'kurse/erste-hilfe-fortbildung': ('Fortbildungstermin finden und buchen', [
  'Zuerst klärst du, wann dein letzter Kurs war. Betriebliche Ersthelfer:innen werden nach der DGUV Vorschrift 1 in der Regel in Zeitabständen von zwei Jahren fortgebildet; der <a href="/auffrischung-rechner/">Auffrischungs-Rechner</a> nennt dir das Fristdatum auf den Tag.',
  'Danach wählst du im <a href="/kursfinder/">Kursfinder</a> den Anlass „Für Job &amp; Betrieb“ und siehst Format, Kostenträger und freie Termine. Die Fortbildung hat denselben Umfang wie die Ausbildung, nämlich neun Unterrichtseinheiten zu 45 Minuten. Wer bei einer verpassten Frist unsicher ist, findet die Auskunft des DGUV-Fachbereichs in den Fragen weiter unten.',
  'Haben mehrere Beschäftigte im Betrieb denselben Fristablauf, lohnt ein gemeinsamer Termin. Ab acht Personen kommen wir bundesweit zu euch; die Anfrage dafür steht unter <a href="/inhouse/#anfrage">Kurs anfragen</a>.'],
  'Quelle: %s (Fortbildung in der Regel alle zwei Jahre, 9 Unterrichtseinheiten zu 45 Minuten).' % FAQ),
 'ratgeber/erste-hilfe-fuehrerschein': ('So meldest du dich für den Führerschein-Kurs an', [
  'Den Kurs für die Fahrerlaubnis buchst du online: Im <a href="/kursfinder/">Kursfinder</a> wählst du „Für den Führerschein“, öffnest die Ausbildung mit neun Unterrichtseinheiten und wählst einen Termin. Mehr als diesen einen Kurs brauchst du dafür nicht.',
  'Beachte beim Anbieter, was die Verordnung verlangt: Der Nachweis wird nach § 19 Abs. 2 FeV durch die Bescheinigung einer amtlich anerkannten Stelle geführt. Die Schulung umfasst mindestens neun Unterrichtseinheiten zu je 45 Minuten und vermittelt auch Grundwissen zur Organ- und Gewebespende. § 19 FeV nennt für die Bescheinigung keine Gültigkeitsfrist.',
  'Keinen Kurs brauchst du, wenn du bereits einen der in § 19 Abs. 3 FeV genannten Nachweise hast, etwa eine ärztliche Staatsprüfung, einen Abschluss in einem Gesundheitsfachberuf oder eine Sanitäts- beziehungsweise rettungsdienstliche Ausbildung. Bei Erweiterung oder Neuerteilung entfällt der Nachweis, wenn du schon einmal teilgenommen hast.'],
  'Quelle: %s, Absätze 1 bis 3 (Stand der Abfrage 19.10.2026).' % FEV),
 'ratgeber/erste-hilfe-kurs-gueltigkeit': ('Welche Frist gilt für dich, und wo findest du den Termin?', [
  'Die Gültigkeit hängt an der Stelle, die den Nachweis verlangt. Für die Fahrerlaubnis ist das die Fahrerlaubnisbehörde, und dort gilt: § 19 FeV nennt für die Bescheinigung keine Gültigkeitsfrist. Für Studium oder Ehrenamt steht die Anforderung nicht in dieser Verordnung. Frage deshalb bei der Hochschule, dem Verein oder dem Veranstalter nach, ob sie ein Höchstalter der Bescheinigung festlegen; im Ratgeber <a href="/ratgeber/erste-hilfe-studium/">Erste Hilfe fürs Studium</a> findest du den Überblick.',
  'Als betriebliche:r Ersthelfer:in gilt dagegen die betriebliche Frist von in der Regel zwei Jahren, als Lehrkraft für Erste Hilfe laufen die Fristen nach dem DGUV Grundsatz 304-003.',
  'Den passenden Termin findest du online im <a href="/kursfinder/">Kursfinder</a>: Anlass wählen, Format und Kostenträger ansehen, Termin buchen. Das Datum deiner nächsten Auffrischung rechnet der <a href="/auffrischung-rechner/">Auffrischungs-Rechner</a> aus.'],
  'Quelle: %s, §&nbsp;19; %s.' % (FEV, FAQ)),
 'inhouse': ('So läuft die Anfrage für Kurse bei euch im Betrieb', [
  'Der Kurs findet bei euch statt, egal wo ihr sitzt: Ab acht Personen reisen wir zu euch, ob Betrieb, Kita, Schule oder Verein. Damit die Rückmeldung mit Terminvorschlag und Preis schnell kommt, helfen drei Angaben im Formular oben: welcher Kurs, wie viele Personen, in welchem Zeitraum.',
  'Welcher Kurs passt, klärt der <a href="/kursfinder/">Kursfinder</a>. Wie viele Ersthelfer:innen ihr benennen müsst, rechnet der <a href="/ersthelfer-rechner/">Ersthelfer-Rechner</a> aus. Wer die Kosten trägt, steht auf der Seite <a href="/kosten/">Kosten &amp; Abrechnung</a>; für benannte Ersthelfer:innen übernimmt in der Regel der Unfallversicherungsträger die Lehrgangsgebühr.',
  'Ist die Gruppe kleiner als acht Personen, stehen auf den Kursseiten offene Termine, die ihr einzeln buchen könnt.'],
  'Quelle: Angaben auf dieser Seite sowie auf <a href="/kosten/">Kosten &amp; Abrechnung</a>.'),
 'kurse/lehrkraefte-ausbildung-tb1': ('Themenbereich 1 buchen und mit Themenbereich 2 zusammen planen', [
  'Themenbereich 1 ist die erste von zwei Stufen. Die Ausbildung zur Lehrkraft für Erste Hilfe besteht aus Themenbereich I mit 24 und Themenbereich II mit 32 Unterrichtseinheiten, zusammen mindestens 56. Für die Anmeldung heißt das: Du buchst zwei getrennte Kurse, und der zweite baut auf dem ersten auf.',
  'Sieh dir deshalb die Termine beider Themenbereiche an, bevor du buchst, und wähle sie so, dass die Reihenfolge stimmt und genug Zeit dazwischen bleibt. Je Ausbildungstag sollen in der Regel nicht mehr als neun Unterrichtseinheiten stattfinden, der Kurs verteilt sich also auf mehrere Tage. Es ist ein Präsenzkurs; den Ort nennt jeder Termin, und bei weiter Anreise planst du Übernachtung ein.',
  'Den Anschluss findest du auf der Seite <a href="/kurse/lehrkraefte-ausbildung-tb2/">Themenbereich 2</a>.'],
  'Quelle: %s (April 2022), Abschnitt 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D3),
 'kurse/betriebssanitaeter-grundausbildung': ('Grundausbildung für Betriebe bundesweit planen', [
  'Wer als Betriebssanitäter:in eingesetzt wird, muss von einer Stelle ausgebildet sein, die die Unfallversicherungsträger als geeignet beurteilt haben (§ 27 Abs. 3 DGUV Vorschrift 1). Sie gliedert sich in zwei Stufen, zuerst die Grundausbildung, danach der Aufbaulehrgang.',
  'Die Grundausbildung umfasst mindestens 63 Unterrichtseinheiten zu 45 Minuten, zuzüglich Prüfungszeit. Da je Tag höchstens neun Unterrichtseinheiten stattfinden dürfen, verteilt sie sich auf mindestens sieben Tage. Das planst du am besten gegen den Aufbaulehrgang: Für den Aufbaulehrgang gilt: Die Grundausbildung darf nicht länger als zwei Jahre zurückliegen.',
  'Betriebe mit mehreren Teilnehmenden aus verschiedenen Standorten fragen den Kurs über „Als Kurs vor Ort anfragen“ an und nennen Personenzahl und Wunschzeitraum. Einzelpersonen wählen einen der Termine oben; den Ort nennt jeder Termin.'],
  'Quelle: %s (April 2022), Abschnitt 1 „Anwendungsbereich“ und 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D2),
 'kurse/lehrkraefte-ausbildung-tb2': ('Themenbereich 2 nach Themenbereich 1 buchen', [
  'Themenbereich 2 umfasst 32 Unterrichtseinheiten zu 45 Minuten und ergänzt Themenbereich 1 mit 24 Einheiten zur vollständigen Ausbildung von mindestens 56 Unterrichtseinheiten. Buche ihn erst, wenn dein Termin für Themenbereich 1 feststeht, und lege beide so, dass die Reihenfolge eingehalten wird.',
  'Der Kurs ist auch später wichtig: Ist deine Lehrberechtigung abgelaufen, ist grundsätzlich wieder eine Grundqualifikation entsprechend Themenbereich II mit mindestens 32 Unterrichtseinheiten nötig. Wer rechtzeitig fortbildet, vermeidet das; die <a href="/kurse/lehrkraefte-fortbildung/">Lehrkräfte-Fortbildung</a> hat dafür mindestens 16 Unterrichtseinheiten.',
  'Je Ausbildungstag sollen in der Regel nicht mehr als neun Unterrichtseinheiten stattfinden. Als Präsenzkurs nennt jeder Termin seinen Ort; wähle einen, der sich gut erreichen lässt, und frage bei einer Gruppe über „Als Kurs vor Ort anfragen“ nach.'],
  'Quelle: %s (April 2022), Abschnitt 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D3),
 'kurse/betriebssanitaeter-aufbaulehrgang': ('Aufbaulehrgang: Zwei-Jahres-Fenster und Anmeldung', [
  'Der Aufbaulehrgang umfasst mindestens 32 Unterrichtseinheiten zu 45 Minuten, zuzüglich Prüfungszeit. Für die Teilnahme darf die Grundausbildung nicht mehr als zwei Jahre zurückliegen. Ausnahme: Hat jemand aufgrund einer anerkannten Qualifikation eine entsprechende berufliche oder ehrenamtliche Tätigkeit ausgeübt, ist deren Ende maßgebend.',
  'Prüfe das Datum deiner Grundausbildung also vor der Buchung und wähle einen Termin innerhalb der Frist. Wenn Betriebe beide Lehrgänge gemeinsam planen, ist die Frist leichter einzuhalten; fragt dazu über „Als Kurs vor Ort anfragen“ an.',
  'Nach dem Abschluss liegt die Verantwortung beim Unternehmen: Es hat dafür zu sorgen, dass Betriebssanitäter:innen regelmäßig innerhalb von drei Jahren fortgebildet werden, mit mindestens 16 Unterrichtseinheiten.'],
  'Quelle: %s (April 2022), Abschnitt 1 „Anwendungsbereich“ und 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D2),
 'branchen/betriebssanitaeter': ('Betriebssanitäter für Betriebe an mehreren Standorten', [
  'Ob ein Betriebssanitäter nötig ist, zeigt der Abschnitt oben. Für die Umsetzung gilt: Eingesetzt werden dürfen nur Personen, die von einer geeigneten Stelle ausgebildet wurden (§ 27 Abs. 3 DGUV Vorschrift 1). Die Ausbildung hat zwei Stufen, Grundausbildung mit mindestens 63 und Aufbaulehrgang mit mindestens 32 Unterrichtseinheiten, jeweils zuzüglich Prüfungszeit.',
  'Weil zwischen Grundausbildung und Aufbaulehrgang höchstens zwei Jahre liegen dürfen und die Fortbildung innerhalb von drei Jahren folgt, lohnt eine gemeinsame Planung. Das gilt besonders für Unternehmen mit mehreren Standorten: Sie schicken Beschäftigte zu offenen Terminen oder bündeln die Teilnehmenden in einem Inhouse-Kurs. Beide Wege sind bundesweit möglich.',
  'Eure Anfrage mit Personenzahl und Wunschzeitraum startet ihr über <a href="/inhouse/#anfrage">Jetzt anfragen</a>.'],
  'Quelle: %s (April 2022), Abschnitt 1 „Anwendungsbereich“ und 2.4.3 „Inhalt und Umfang der Lehrgänge“.' % D2),
}

CTA = '<section class="section"><div class="wrap">\n<div class="cta-band'
ART = '\n</div>\n<aside class="ratgeber-cta'
HID = '<section class="section soft" hidden>'


def words(html):
    return len(re.sub(r'<[^>]+>', ' ', html).replace('&amp;', '&').replace('&nbsp;', ' ').split())


def block(slug, h2, ps, q):
    inner = '<h2>%s</h2>' % h2 + ''.join('<p>%s</p>' % p for p in ps)
    n = words(inner)
    assert 100 <= n <= 160, (slug, n)
    q = '<p class="muted">%s</p>' % q
    if slug.startswith('ratgeber/'):
        return '<div id="top15-2b">' + inner + q + '</div>', n
    return '<section class="section" id="top15-2b"><div class="wrap article">' + inner + q + '</div></section>\n\n', n


def anchor(slug, s):
    if slug.startswith('ratgeber/'):
        a = ART
    elif slug == 'inhouse':
        a = HID
    else:
        a = CTA
    i = s.rfind(a)
    assert i >= 0 and (a != ART or s.count(a) == 1), (slug, a)
    return i


for slug, (h2, ps, q) in T.items():
    f = slug + '/index.html'
    s = open(f, encoding='utf-8').read()
    if 'id="top15-2b"' in s:
        print('schon da', slug)
        continue
    b, n = block(slug, h2, ps, q)
    i = anchor(slug, s)
    s = s[:i] + b + s[i:]
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(m)
    assert s.count('id="top15-2b"') == 1
    open(f, 'w', encoding='utf-8').write(s)
    print('ok', slug, n)

# sitemap: nur lastmod der 10 Seiten
SM = 'sitemap.xml'
x = open(SM, encoding='utf-8').read()
for slug in T:
    loc = 'https://www.erstehilfekurse.online/%s/' % slug
    pat = re.compile(r'(<loc>%s</loc><lastmod>)[^<]*(</lastmod>)' % re.escape(loc))
    assert len(pat.findall(x)) == 1, slug
    x = pat.sub(r'\g<1>2026-10-19\g<2>', x)
open(SM, 'w', encoding='utf-8').write(x)
print('sitemap ok')
