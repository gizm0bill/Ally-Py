define(['backbone'], function(Backbone) {


    var Router = {
        hasRoute: Backbone.history.start({root: config.lib_url + 'start.html'}),

        /**
         * Add route to global router and try to active it
         * if there was no route matching current fragment.
         */
        route: function(route, name, callback) {
            var router = new Backbone.Router();
            router.route(route, name, callback);
            if (!this.hasRoute) {
                this.hasRoute = Backbone.history.loadUrl();
            }
        }
    };

    return Router;
});
