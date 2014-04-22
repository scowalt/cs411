<?php
session_start();

require_once './vendor/autoload.php';
require_once './encryption.php';
require_once './config.php';

// setup twig
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

$_SESSION['auth_state'] = encrypt_state('test');

// setup google client
$client = new Google_Client();
$client->setClientId($client_id);
$client->setClientSecret($client_secret);
$client->setRedirectUri($redirect_uri = 'http://' . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF']);
$client->setScopes('email'); // need this to confirm netID

/************************************************
  If we're logging out we just need to clear our
  local access token in this case
 ************************************************/
if (isset($_REQUEST['logout'])) {
  unset($_SESSION['access_token']);
  unset($_SESSION['user_email']);
  echo "Logged out";
  die;
}

/************************************************
  If we have a code back from the OAuth 2.0 flow,
  we need to exchange that with the authenticate()
  function. We store the resultant access token
  bundle in the session, and redirect to ourself.
 ************************************************/
if (isset($_GET['code'])) {
  $client->authenticate($_GET['code']);
  $_SESSION['access_token'] = $client->getAccessToken();
  $token_data = $client->verifyIdToken()->getAttributes();
  $_SESSION['user_email'] = $token_data['payload']['email'];
  echo "All done<br/>" . 
    $_SESSION['user_email'] . 
    "<br/>" . $_SESSION['auth_state'] . 
    "<br/>" . decrypt_state($_SESSION['auth_state']);
}

/************************************************
  If we have an access token, we can make
  requests, else we redirect user to an 
  authentication URL.
 ************************************************/
if (isset($_SESSION['access_token']) && $_SESSION['access_token']) {
  $client->setAccessToken($_SESSION['access_token']);
} else {
  $authUrl = $client->createAuthUrl();
  header('Location: ' . filter_var($authUrl, FILTER_SANITIZE_URL));
}

/************************************************
  If we're signed in we can go ahead and retrieve
  the ID token, which is part of the bundle of
  data that is exchange in the authenticate step
  - we only need to do a network call if we have
  to retrieve the Google certificate to verify it,
  and that can be cached.
 ************************************************/
if ($client->getAccessToken()) {
  $_SESSION['access_token'] = $client->getAccessToken();
  $token_data = $client->verifyIdToken()->getAttributes();
  $_SESSION['user_id'] = $token_data;
}

?>