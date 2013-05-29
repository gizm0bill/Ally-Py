define(['angular', 'utils/route-config', 'controllers/home', 'services/action'], 
function (angular, routeConfig, Home, Action) 
{
    'use strict';
    
    var m = angular.module('myApp', [], function ($compileProvider, $controllerProvider) {
        routeConfig.setCompileProvider($compileProvider);
        routeConfig.setControllerProvider($controllerProvider);
    });
    
    m.controller('Home', Home);
    Home.$inject = ['ActionService'];
    
    return m;
});
