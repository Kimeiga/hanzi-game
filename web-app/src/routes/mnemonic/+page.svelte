<script lang="ts">
	import { onMount } from 'svelte';
	import type { MnemonicGameData, MnemonicGameState } from '$lib/mnemonicTypes';
	import {
		loadMnemonicData,
		initializeMnemonicGame,
		checkAnswer,
		nextRound
	} from '$lib/mnemonicLogic';

	let gameData = $state<MnemonicGameData | null>(null);
	let gameState = $state<MnemonicGameState | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let inputRef = $state<HTMLInputElement | null>(null);

	onMount(async () => {
		try {
			const data = await loadMnemonicData();
			gameData = data;
			gameState = initializeMnemonicGame(data);
			loading = false;
			// Focus input after mount
			setTimeout(() => inputRef?.focus(), 100);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load game data';
			loading = false;
		}
	});

	function handleSubmit(e: Event) {
		e.preventDefault();
		if (!gameState || !gameData) return;

		const isCorrect = checkAnswer(gameState.userAnswer, gameState.currentQuestion, gameData);

		if (isCorrect) {
			gameState.won = true;
			gameState.score += 10 + gameState.streak * 2;
			gameState.streak += 1;
			gameState.feedback = `✅ Correct! +${10 + (gameState.streak - 1) * 2} points`;
		} else {
			gameState.attemptsLeft--;
			if (gameState.attemptsLeft <= 0) {
				gameState.gameOver = true;
				gameState.showAnswer = true;
				gameState.streak = 0;
				gameState.feedback = `❌ The answer was: ${gameState.currentQuestion.targetMeaning}`;
			} else {
				gameState.feedback = `❌ Try again! ${gameState.attemptsLeft} attempts left`;
			}
		}
	}

	function handleNextRound() {
		if (!gameState || !gameData) return;
		gameState = nextRound(gameState, gameData);
		setTimeout(() => inputRef?.focus(), 100);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && (gameState?.won || gameState?.gameOver)) {
			handleNextRound();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="mnemonic-game">
	{#if loading}
		<div class="loading">Loading mnemonic game...</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if gameState}
		<!-- Header -->
		<header class="game-header">
			<a href="/" class="back-link">← Back to Builder</a>
			<div class="level-info">HSK Level {gameState.currentLevel}</div>
			<div class="round-info">Round {gameState.currentRound}</div>
			<div class="score-info">Score: {gameState.score}</div>
			{#if gameState.streak > 1}
				<div class="streak-info">🔥 {gameState.streak} streak!</div>
			{/if}
		</header>

		<!-- Equation Display -->
		<div class="equation-container">
			<h2 class="equation-label">What character means:</h2>
			<div class="equation">
				{#each gameState.currentQuestion.componentNames as name, i}
					<span class="component-name">{name}</span>
					{#if i < gameState.currentQuestion.componentNames.length - 1}
						<span class="plus">+</span>
					{/if}
				{/each}
			</div>
			<div class="components-hint">
				({gameState.currentQuestion.components.join(' ')})
			</div>
		</div>

		<!-- Answer Input -->
		<form class="answer-form" onsubmit={handleSubmit}>
			<input
				type="text"
				bind:value={gameState.userAnswer}
				bind:this={inputRef}
				placeholder="Type the meaning..."
				disabled={gameState.won || gameState.gameOver}
				class="answer-input"
				class:correct={gameState.won}
				class:incorrect={gameState.gameOver && !gameState.won}
			/>
			{#if !gameState.won && !gameState.gameOver}
				<button type="submit" class="submit-btn">Check</button>
			{/if}
		</form>

		<!-- Feedback -->
		{#if gameState.feedback}
			<div class="feedback" class:success={gameState.won} class:error={gameState.gameOver && !gameState.won}>
				{gameState.feedback}
			</div>
		{/if}

		<!-- Show character on win/lose -->
		{#if gameState.won || gameState.gameOver}
			<div class="reveal">
				<div class="reveal-character">{gameState.currentQuestion.targetCharacter}</div>
				<div class="reveal-meaning">{gameState.currentQuestion.targetMeaning}</div>
			</div>
			<button class="next-btn" onclick={handleNextRound}>
				Next Round →
			</button>
		{/if}

		<!-- Attempts indicator -->
		<div class="attempts">
			Attempts: {'❤️'.repeat(gameState.attemptsLeft)}{'🖤'.repeat(gameState.maxAttempts - gameState.attemptsLeft)}
		</div>
	{/if}
</div>

<style>
	.mnemonic-game {
		max-width: 600px;
		margin: 0 auto;
		padding: 20px;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		min-height: 100vh;
		background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
		color: #eee;
	}

	.loading, .error {
		text-align: center;
		padding: 40px;
		font-size: 1.2em;
	}

	.error { color: #ff6b6b; }

	.game-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 30px;
		padding-bottom: 15px;
		border-bottom: 1px solid #333;
	}

	.back-link {
		color: #64b5f6;
		text-decoration: none;
		font-size: 0.9em;
	}

	.back-link:hover { text-decoration: underline; }

	.level-info, .round-info, .score-info {
		background: #2d2d44;
		padding: 5px 12px;
		border-radius: 20px;
		font-size: 0.9em;
	}

	.streak-info {
		background: linear-gradient(135deg, #ff6b6b, #feca57);
		color: #000;
		padding: 5px 12px;
		border-radius: 20px;
		font-weight: bold;
	}

	.equation-container {
		text-align: center;
		margin: 40px 0;
	}

	.equation-label {
		font-size: 1.1em;
		color: #888;
		margin-bottom: 20px;
	}

	.equation {
		display: flex;
		justify-content: center;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px;
		font-size: 1.5em;
		margin-bottom: 15px;
	}

	.component-name {
		background: linear-gradient(135deg, #667eea, #764ba2);
		padding: 10px 20px;
		border-radius: 10px;
		font-weight: bold;
	}

	.plus {
		color: #888;
		font-size: 1.2em;
	}

	.components-hint {
		color: #666;
		font-size: 1.2em;
		letter-spacing: 3px;
	}

	.answer-form {
		display: flex;
		gap: 10px;
		justify-content: center;
		margin: 30px 0;
	}

	.answer-input {
		flex: 1;
		max-width: 300px;
		padding: 15px 20px;
		font-size: 1.2em;
		border: 2px solid #444;
		border-radius: 10px;
		background: #2d2d44;
		color: #fff;
		text-align: center;
	}

	.answer-input:focus {
		outline: none;
		border-color: #667eea;
	}

	.answer-input.correct { border-color: #4ecdc4; background: #1a3a38; }
	.answer-input.incorrect { border-color: #ff6b6b; background: #3a1a1a; }

	.submit-btn, .next-btn {
		padding: 15px 30px;
		font-size: 1.1em;
		border: none;
		border-radius: 10px;
		cursor: pointer;
		font-weight: bold;
		transition: transform 0.1s;
	}

	.submit-btn {
		background: linear-gradient(135deg, #667eea, #764ba2);
		color: white;
	}

	.next-btn {
		background: linear-gradient(135deg, #4ecdc4, #44a08d);
		color: white;
		display: block;
		margin: 20px auto;
	}

	.submit-btn:hover, .next-btn:hover { transform: scale(1.05); }

	.feedback {
		text-align: center;
		padding: 15px;
		border-radius: 10px;
		margin: 20px 0;
		font-size: 1.1em;
	}

	.feedback.success { background: #1a3a38; color: #4ecdc4; }
	.feedback.error { background: #3a1a1a; color: #ff6b6b; }

	.reveal {
		text-align: center;
		margin: 30px 0;
	}

	.reveal-character {
		font-size: 5em;
		margin-bottom: 10px;
	}

	.reveal-meaning {
		font-size: 1.5em;
		color: #888;
	}

	.attempts {
		text-align: center;
		font-size: 1.5em;
		margin-top: 30px;
	}
</style>

