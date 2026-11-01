<?php
// OVAIC membership application: validate, store outside the web root, notify the Board, confirm to the applicant.
declare(strict_types=1);

// Mail addresses live outside the web root and outside the public repository (no addresses in public, against spam).
$OVAIC_CFG = (array) (@include dirname(__DIR__) . '/ovaic-config.php');
define('OVAIC_FROM', (string) ($OVAIC_CFG['from'] ?? ''));
define('OVAIC_TO', (string) ($OVAIC_CFG['to'] ?? ''));
const LANGS = ['en', 'de', 'fr', 'it', 'es', 'pt', 'ru', 'uk', 'be', 'pl', 'cs', 'sk', 'sl', 'sr', 'hu', 'lv', 'lt', 'et', 'sv', 'no', 'ja', 'ko'];
const SIZES = ['Individual (observer): 100', 'Up to 5 staff, non profit, university: 300', '6 to 19 staff: 800',
    '20 to 49 staff: 1,500', '50 to 249 staff: 3,000', '250 to 999 staff: 5,000', 'Strategic, 1,000 to 9,999 staff: 50,000',
    'Strategic, 10,000 staff or more: from 100,000 by agreement'];
const PAYS = ['Stablecoin (Ethereum)', 'Bank transfer', 'Bitcoin', 'PayPal'];
const CONFIRM = [
    'en' => ['Your OVAIC application', "Thank you for applying to the Open Verifiable AI Consortium (OVAIC).\n\nWe have received your application. The Board decides within 60 days and will reply by email.\n\nOVAIC, Zurich\nhttps://ovaic.org"],
    'de' => ['Ihr Antrag bei OVAIC', "Danke für Ihren Antrag beim Open Verifiable AI Consortium (OVAIC).\n\nIhr Antrag ist eingegangen. Der Vorstand entscheidet innert 60 Tagen und antwortet per E-Mail.\n\nOVAIC, Zürich\nhttps://ovaic.org"],
    'fr' => ['Votre candidature à OVAIC', "Merci pour votre candidature à l'Open Verifiable AI Consortium (OVAIC).\n\nNous avons bien reçu votre candidature. Le comité décide dans les 60 jours et vous répondra par courriel.\n\nOVAIC, Zurich\nhttps://ovaic.org"],
    'it' => ['La vostra domanda a OVAIC', "Grazie per la vostra domanda all'Open Verifiable AI Consortium (OVAIC).\n\nAbbiamo ricevuto la domanda. Il comitato decide entro 60 giorni e risponderà per email.\n\nOVAIC, Zurigo\nhttps://ovaic.org"],
    'es' => ['Su solicitud a OVAIC', "Gracias por su solicitud al Open Verifiable AI Consortium (OVAIC).\n\nHemos recibido su solicitud. La Junta decide en 60 días y le responderá por correo electrónico.\n\nOVAIC, Zúrich\nhttps://ovaic.org"],
    'ja' => ['OVAIC への申請', "Open Verifiable AI Consortium (OVAIC) にお申し込みいただきありがとうございます。\n\n申請を受け付けました。理事会は60日以内に決定し、電子メールでお知らせします。\n\nOVAIC、チューリッヒ\nhttps://ovaic.org"],
];

function back(string $lang, string $q): void {
    $base = $lang === 'en' ? '/' : "/$lang/";
    header('Location: ' . $base . 'join/?' . $q, true, 303);
    exit;
}

function clean(string $k, int $max = 2000): string {
    $v = trim((string)($_POST[$k] ?? ''));
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/u', '', $v) ?? '';
    return mb_substr($v, 0, $max);
}

function send(string $to, string $subject, string $body, string $replyTo = OVAIC_FROM): void {
    $headers = "From: OVAIC <" . OVAIC_FROM . ">\r\nReply-To: " . $replyTo .
               "\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";
    @mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f' . OVAIC_FROM);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { back('en', ''); }
$lang = in_array($_POST['lang'] ?? '', LANGS, true) ? $_POST['lang'] : 'en';

// spam: honeypot filled or form sent faster than 3 seconds
$t0 = (int)($_POST['t0'] ?? 0);
if (clean('website2') !== '' || $t0 === 0 || (microtime(true) * 1000 - $t0) < 3000) { back($lang, 'sent=1'); }

$req = ['org', 'legal_form', 'country', 'city', 'web', 'name', 'role', 'email', 'work', 'products', 'owners', 'relations'];
$a = [];
foreach (array_merge($req, ['uid', 'phone', 'testcase', 'note']) as $k) { $a[$k] = clean($k); }
$a['category'] = in_array($_POST['category'] ?? '', ['member', 'observer'], true) ? $_POST['category'] : '';
$size = filter_var($_POST['size'] ?? '', FILTER_VALIDATE_INT, ['options' => ['min_range' => 0, 'max_range' => count(SIZES) - 1]]);
$pay = filter_var($_POST['pay'] ?? '', FILTER_VALIDATE_INT, ['options' => ['min_range' => 0, 'max_range' => count(PAYS) - 1]]);
$a['size'] = $size === false ? '' : SIZES[$size];
$a['pay'] = $pay === false ? '' : PAYS[$pay];
$a['support'] = !empty($_POST['support']);
$a['reduce'] = !empty($_POST['reduce']);

$ok = $a['category'] !== '' && $a['size'] !== '' && filter_var($a['email'], FILTER_VALIDATE_EMAIL)
    && !empty($_POST['c_sanctions']) && !empty($_POST['c_accept']) && !empty($_POST['c_privacy']);
foreach ($req as $k) { if ($a[$k] === '') { $ok = false; } }
if (!$ok) { back($lang, 'error=1'); }

$a['lang'] = $lang;
$a['received'] = gmdate('c');
$a['confirmed'] = ['sanctions' => true, 'accept' => true, 'privacy' => true];

$dir = dirname(__DIR__) . '/ovaic';
if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
@file_put_contents($dir . '/applications.jsonl', json_encode($a, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND | LOCK_EX);

$lines = [];
foreach ($a as $k => $v) {
    if (is_array($v)) { $v = 'yes'; } elseif (is_bool($v)) { $v = $v ? 'yes' : 'no'; }
    $lines[] = str_pad($k, 12) . ': ' . str_replace("\n", "\n              ", (string)$v);
}
send(OVAIC_TO, 'OVAIC application: ' . $a['org'], "New membership application\n\n" . implode("\n", $lines) . "\n", $a['email']);
[$subj, $body] = CONFIRM[$lang] ?? CONFIRM['en'];  // newer languages get the English confirmation
send($a['email'], $subj, $body);

back($lang, 'sent=1');
