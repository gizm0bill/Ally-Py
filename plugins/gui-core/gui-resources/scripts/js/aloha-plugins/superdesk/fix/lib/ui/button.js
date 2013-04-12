/**
 * NOTES:
 *    - Why do we maintain 2 references to the DOM element for a button
 *    component (this.element = this.buttonElement)?
 */

define([
	'jquery',
	'ui/button'
],
function ($, Button) 
{
	'use strict';
	
	var // save original button constructor
	    origInit = Button.prototype.init,
	    // save original tooltip
	    origTooltip = $.fn.tooltip;
	
	Button.prototype.init = function()
	{
	    // apply original constructor
	    origInit.apply(this, arguments);
	    // apply original tooltip after we avoid the "close" option
	    this.buttonElement.tooltip = function()
	    { 
	        if( arguments[0] == 'close' ) return false; 
	        origTooltip.apply(this, arguments);
	    };
	};
	return Button;
});
