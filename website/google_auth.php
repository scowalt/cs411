<?php
session_start();

require_once './vendor/autoload.php';
require_once './encryption.php';
require_once './config.php';

// setup twig
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

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
  logout();
  header("refresh:3;url=index.php");
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
  if (strval($_SESSION['auth_state']) !== strval($_GET['state'])) {
    die('The session state did not match.' .
      '<br/>' . strval($_SESSION['auth_state'])
      . '<br/>' . strval($_GET['state'])
      . '<br/>' . decrypt_state(strval($_GET['state'])));
  }
  $client->authenticate($_GET['code']);
  $_SESSION['access_token'] = $client->getAccessToken();
  $token_data = $client->verifyIdToken()->getAttributes();
  $_SESSION['user_email'] = $token_data['payload']['email'];
  if (!illinois_email($token_data['payload']['email'])){
    logout();
    header("refresh:3;url=google_auth.php");
    echo "Not an Illinois email address. Please try again";
    die;
  }
  add_user(netidOf($token_data['payload']['email']));
  header('Location: '. 'http://' . $_SERVER['HTTP_HOST'] . '/' . decrypt_state(strval($_GET['state'])) .'.php');

}

/************************************************
  If we have an access token, we can make
  requests, else we redirect user to an 
  authentication URL.
 ************************************************/
if (user_has_access_token()) {
  $client->setAccessToken($_SESSION['access_token']);
} else {
  $_SESSION['auth_state'] = get_state();
  $client->setState(get_state());
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
  $_SESSION['user_email'] = $token_data['payload']['email'];
  if (!illinois_email($token_data['payload']['email'])){
    logout();
    header("refresh:3;url=google_auth.php");
    echo "Not an Illinois email address. Please try again";
    die;
  }
  header('Location: '. 'http://' . $_SERVER['HTTP_HOST'] . '/' . decrypt_state(get_state()) .'.php');
}

function user_has_access_token(){
  return (isset($_SESSION['access_token']) && $_SESSION['access_token'] 
  && json_encode($_SESSION['access_token']) !== '"[]"');
}

// get the (encrypted) redirect page name
function get_state(){
  $state = 'index'; // default redirect page
  if (isset($_GET['redirect']) && $_GET['redirect']){
    $state = $_GET['redirect'];
  }
  return encrypt_state($state);
}

// given netid@illinois.edu, return netid
function netidOf($email){
  return substr($email, 0, (strlen($email) - 13));
}

// confirm an email address is @illinios.edu
function illinois_email($email){
  return (strpos($email, "@illinois.edu")) !== false;
}

// remove user session information
function logout(){
  unset($_SESSION['access_token']);
  unset($_SESSION['user_email']);
  unset($_SESSION['auth_state']);
}

// add user with netid to database
function add_user($netid){
  // connect to database
  $link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
  if (!$link) {
      die('Not connected : ' . mysql_error());
  }
  mysql_select_db('cs411backend_food', $link);

  // add user to database
  $query = "INSERT IGNORE INTO users (user_net_id) VALUES (\"$netid\")";
  return $result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());;
}

?>