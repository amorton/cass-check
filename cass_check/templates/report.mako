<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Cassandra Checkup Report XX-TIME-XX</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le HTML5 shim, for IE6-8 support of HTML elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le styles -->
    <link href="assets/bootstrap.min.css" rel="stylesheet">

    <!-- Le fav and touch icons -->
    <!-- 
    <link rel="shortcut icon" href="/static/images/favicon.ico">
    <link rel="apple-touch-icon" href="/static/images/apple-touch-icon.png">
    <link rel="apple-touch-icon" sizes="72x72" href="/static/images/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="114x114" href="/static/images/apple-touch-icon-114x114.png">
    -->
  </head>

  <body >

    <div class="navbar" data-dropdown="dropdown">
      <div class="navbar-inner">
        <div class="container">
          <a class="brand" href="/">Cassandra Checkup</a>
        </div>
      </div>
    </div>
    
    <div class="container">
      <table class="table table-striped">
        <caption>Cassandra Checkup output for XX TIME XX</caption>
        <thead>
          <tr>
            <th>Task</th>
            <th>Output</th>
          </tr>
        </thead>
        <tbody>
          % for receipt, files in receipt_files.iteritems():
            <tr>
              <td>
                  ${receipt.name}
              </td>
              <td>
                % if receipt.error:
                  <span class="label label-important">Error</span>
                  ${receipt.error}
                % else:
                  <ul>
                    % for file_name in files:
                      <li>
                        <a href="${file_name}">${file_name}</a>
                      </li>
                    %endfor
                  </ul>
                %endif
              </td>
            </tr>
          % endfor
        </tbody>
      </table>

    </div>
    
    <script src="assets/jquery-1.8.3.min.js"></script>
    <script src="assets/bootstrap.min.js"></script>
  </body>
</html>
