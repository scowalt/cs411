<?php

require_once './config.php';

// http://stackoverflow.com/a/9262137/1222411
function encrypt_state($state){
	return base64_encode(mcrypt_encrypt(MCRYPT_RIJNDAEL_256, md5($key), $state, MCRYPT_MODE_CBC, md5(md5($STATE_ENCRYPTION_KEY))));
}

// http://stackoverflow.com/a/9262137/1222411
function decrypt_state($encrypted){
	return rtrim(mcrypt_decrypt(MCRYPT_RIJNDAEL_256, md5($key), base64_decode($encrypted), MCRYPT_MODE_CBC, md5(md5($STATE_ENCRYPTION_KEY))), "\0");
}

?>