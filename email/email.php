<?php

$to = 'scowalt@gmail.com';
$subject = 'Automated email';
$message = 'testing 123';
$headers = 'From: Food' . "\r\n" . 
    'X-Mailer: PHP/' . phpversion();

mail($to, $subject, $message, $headers);

?>