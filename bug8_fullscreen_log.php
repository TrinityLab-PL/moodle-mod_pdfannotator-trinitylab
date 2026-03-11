<?php
define('MOODLE_INTERNAL', 1);
$root = __DIR__;
$logDir = $root . '/_staging';
if (!is_dir($logDir)) { @mkdir($logDir, 0777, true); }
$logFile = $logDir . '/bug8_fullscreen_console.log';
$raw = file_get_contents('php://input');
if ($raw === false) { $raw = ''; }
$ts = date('Y-m-d H:i:s');
$line = $ts . ' ' . $raw . "\n";
@file_put_contents($logFile, $line, FILE_APPEND);
header('Content-Type: application/json');
echo json_encode(['status' => 'ok']);
