define(['app', 'utils/route-config'], function (app, routeConfig) 
{
    'use strict';
    
    return app.config(function ($routeProvider) 
    {
        $routeProvider
            .when('/', routeConfig.config('../templates/dashboard.html', 'controllers/home'))
            .when('/login', routeConfig.config('../templates/login.html', 'controllers/login'))
            .otherwise({redirectTo:'/'});
    });

    return app;
});
