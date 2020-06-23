// Interval between repeated requests in ms
var request_interval = 300

/*
	Send post request to game

	@arg data - object (dict) with data to send in request
	@arg callback - function to call after request is done,
					must accept 1 parameter (response in parsed JSON format)
*/
function gamePost(data, callback){
	var xhr = new XMLHttpRequest();
	xhr.open("POST", location.href, true);
	xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			// Response must always be JSON. If it isn't, there was an error
			try {
				JSON.parse(xhr.responseText);
			} catch (e) {
				alert('Something went wrong! Try reloading the page');
				return false;
			}
			callback(JSON.parse(xhr.responseText));
		}
	}
	xhr.send(JSON.stringify(data));
}

/*
	Increase counter of current player's active cells

	@arg counts_class - class of sought-for elem
*/
function incCount(counts_class) {
	var counts_elem = $('.' + counts_class);
	if (counts_elem.length == 1) {
		counts_elem.html(parseInt(counts_elem.html()) + 1);
	}
}

/*
	Get "numbers" (calculations) view of gameboard

	@ret gameboard - Y*X matrix of ints representing cells' states
*/
function calcGameboard() {
	gameboard = [];
	$('.gameboard .row').each(function(){
		row = [];
		$(this).find('.cell').each(function(){
			row.push($(this).data('cell'));
		})
		gameboard.push(row);
	})

	return gameboard;
}


/*
████─████─█───█─███────█───████─████─████
█────█──█─██─██─█──────█───█──█─█──█─█──█
█─██─████─█─█─█─███────█───█──█─█──█─████
█──█─█──█─█───█─█──────█───█──█─█──█─█
████─█──█─█───█─███────███─████─████─█
*/

/*
	Check if P2 added to game
	Move to next step if yes
	Otherwise repeat after interval
*/
function checkP2(){
	gamePost({'action': 'check_p2'}, function(response){
		if (response.p2_ingame) {
			updateGameStatus();
		} else {
			setTimeout(checkP2, request_interval);
		}
	})
}

/*
	Request for 'idle' phase, repeats until phase changes
	Update game status text and cells counters
	If necessary, reload gameboard
	Once phase changes, alert player
*/
function updateGameStatus(){
	post_data = {
		'action': 'get_status',
		'gameboard': JSON.stringify(calcGameboard())
	}
	gamePost(post_data, function(response){
		$('._gamestatus').html(response.status);
		$('._p1_cells').html(response.p1_cells);
		$('._p2_cells').html(response.p2_cells);
		if (response.gameboard) {
			$('._gameboard_wrapper').html(response.gameboard);
		}
		switch (response.next_action) {
			case 'wait':
				setTimeout(updateGameStatus, request_interval);
				break;
			case 'add_cell':
				alert('Your turn to add cells! Good luck!');
				break;
			case 'game_over':
				alert('Game over! Thanks for playing!');
				break;
		}
	})
}

/*
	Handler of putting life into dead cell
	After necessary amount of cells added, switch to idle phase
*/
$('._gamemain').on('click', '.gameboard._mod-addcell .cell-dead', function(){
	var $this = $(this);
	post_data = {
		'action': 'add_cell',
		'cell_x': $this.data('x'),
		'cell_y': $this.data('y')
	}
	gamePost(post_data, function(response){
		if (response.error) {
			alert(response.message);
			return false;
		}
		
		incCount(response.counts_class);
		$this.removeClass('cell-dead').addClass(response.cell_class);
		$('._gamestatus').html(response.status);
		switch (response.next_action) {
			case 'wait':
				$('.gameboard._mod-addcell').removeClass('_mod-addcell');
				if (response.send_gen_move) {
					$.ajax({
						type: "POST",
						url: location.href,
						headers: {'Content-type': 'application/json; charset=utf-8'},
						data: JSON.stringify({'action': 'gen_move'})
					})
				}
				setTimeout(updateGameStatus, request_interval);
				break;
		}
	})
})


// Game cycle start
checkP2();