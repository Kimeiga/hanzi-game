<script lang="ts">
	import { onMount } from 'svelte';
	import type { GameData, GameState, Card } from '$lib/types';
	import {
		loadGameData,
		initializeGameState,
		findPossibleCombinations,
		combineCards,
		decomposeCard,
		checkAnswer,
		nextRound,
		useHint,
		regenerateHints,
		getComponentsWithDecoys,
		createCardsFromComponents,
		generateHints
	} from '$lib/gameLogic';

	let gameData = $state<GameData | null>(null);
	let gameState = $state<GameState | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let message = $state<string | null>(null);
	let highlightedCardIds = $state<Set<string>>(new Set());

	onMount(async () => {
		try {
			const data = await loadGameData();
			gameData = data;

			// Check for word query parameter
			const urlParams = new URLSearchParams(window.location.search);
			const testWord = urlParams.get('word');

			if (testWord) {
				// Initialize game with specific word for testing
				gameState = initializeGameStateWithWord(data, testWord);
			} else {
				gameState = initializeGameState(data);
			}

			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load game data';
			loading = false;
		}
	});

	// Helper function to initialize game with a specific word
	function initializeGameStateWithWord(data: GameData, targetWord: string): GameState {
		const hskLevel = 1; // Default to HSK 1 for testing

		// Get components from 3 words: target + 2 decoys
		const { components, decoyWords } = getComponentsWithDecoys(targetWord, hskLevel, data);
		const cards = createCardsFromComponents(components, data);

		// Get definitions for the target word (join array into string)
		// Use character glosses for single characters (includes top words with underscores)
		const isSingleChar = targetWord.length === 1;
		const definitions = isSingleChar
			? data.charGlosses?.[targetWord]
			: data.wordGlosses?.[targetWord];
		const targetGloss = definitions && definitions.length > 0
			? definitions.join('; ')
			: `Word: ${targetWord}`;

		// Generate smart hints
		const hints = generateHints(targetWord, cards, data);

		console.log('🎮 Test mode - initialized with word:', {
			targetWord,
			targetGloss,
			decoyWords,
			componentCount: components.length,
			allComponents: components,
			hintsGenerated: hints.length
		});

		return {
			currentLevel: hskLevel,
			roundsPerLevel: 2,
			currentRound: 1,
			totalRoundsCompleted: 0,
			targetWord,
			targetGloss,
			availableCards: cards,
			selectedCards: [],
			possibleCombinations: [],
			attemptsLeft: 3,
			maxAttempts: 3,
			gameOver: false,
			won: false,
			hints,
			hintsUsed: 0,
			totalHintsUsed: 0
		};
	}

	function toggleCardSelection(card: Card) {
		if (!gameState) return;

		const isSelected = gameState.selectedCards.some((c) => c.id === card.id);

		if (isSelected) {
			// Deselect
			gameState.selectedCards = gameState.selectedCards.filter((c) => c.id !== card.id);
		} else {
			// Select
			gameState.selectedCards = [...gameState.selectedCards, card];
		}

		// Update possible combinations
		if (gameData) {
			gameState.possibleCombinations = findPossibleCombinations(gameState.selectedCards, gameData);
		}
	}

	function handleCombine(targetChar: string) {
		if (!gameState || !gameData) return;

		gameState.availableCards = combineCards(
			gameState.selectedCards,
			targetChar,
			gameState.availableCards,
			gameData
		);

		gameState.selectedCards = [];
		gameState.possibleCombinations = [];

		// Regenerate hints based on new available cards
		// Now that hints are state-aware, they'll show the next valid steps
		gameState = regenerateHints(gameState, gameData);

		// Clear message and highlights when combining
		message = null;
		highlightedCardIds = new Set();
	}

	function handleDecompose(card: Card) {
		if (!gameState || !gameData) return;

		gameState.availableCards = decomposeCard(card, gameState.availableCards, gameData);
		gameState.selectedCards = [];
		gameState.possibleCombinations = [];

		// Regenerate hints based on new available cards
		// Now that hints are state-aware, they'll show the next valid steps
		gameState = regenerateHints(gameState, gameData);

		// Clear message and highlights when decomposing
		message = null;
		highlightedCardIds = new Set();
	}

	function handleSubmit() {
		if (!gameState || !gameData) return;

		const isCorrect = checkAnswer(gameState.availableCards, gameState.targetWord);

		if (isCorrect) {
			gameState.won = true;

			// Remove the target word from available cards
			gameState.availableCards = gameState.availableCards.filter(
				card => card.character !== gameState.targetWord
			);

			// Clear selections and highlights
			gameState.selectedCards = [];
			gameState.possibleCombinations = [];
			highlightedCardIds = new Set();
			message = null;
		} else {
			gameState.attemptsLeft--;
			if (gameState.attemptsLeft <= 0) {
				gameState.gameOver = true;
				message = `❌ Game Over! The answer was: ${gameState.targetWord}`;
			} else {
				message = `❌ Incorrect! ${gameState.attemptsLeft} attempts left`;
			}
		}
	}

	function handleNextRound() {
		if (!gameState || !gameData) return;
		gameState = nextRound(gameState, gameData);
		message = null;
		highlightedCardIds = new Set();
	}

	function handleHint() {
		if (!gameState || !gameData) return;

		console.log('🔍 HINT BUTTON CLICKED');
		console.log('Available hints:', gameState.hints);
		console.log('Unused hints:', gameState.hints.filter(h => !h.used));

		const result = useHint(gameState);
		if (!result.hint) {
			console.log('❌ No hint returned from useHint()');
			message = '❌ No more hints available!';
			return;
		}

		console.log('💡 Hint returned:', result.hint);

		// Update game state
		gameState = result.state;

		// Highlight the hinted cards (stays until dismissed)
		highlightedCardIds = new Set(result.hint.cardIds);
		console.log('Highlighted card IDs:', Array.from(highlightedCardIds));

		// Show hint message (stays until dismissed)
		if (result.hint.isAnswer) {
			message = `✨ Hint: This is the answer! Just submit it!`;
		} else {
			message = `💡 Hint: Try combining these highlighted components!`;
		}
	}

	function resetGame() {
		if (!gameData) return;
		gameState = initializeGameState(gameData);
		message = null;
		error = null;
	}

	/**
	 * Convert a character to GlyphWiki URL
	 * Handles both Unicode characters and special entity references like &CDP-855B;
	 */
	function getGlyphWikiUrl(char: string): string {
		// Check if it's an entity reference like &CDP-855B; or &AJ1-12345;
		if (char.startsWith('&') && char.endsWith(';')) {
			const entity = char.slice(1, -1); // Remove & and ;

			// Handle CDP (Chinese Document Processing) references
			if (entity.startsWith('CDP-')) {
				const hex = entity.substring(4).toLowerCase(); // Get hex part after "CDP-"
				return `https://glyphwiki.org/glyph/cdp-${hex}.svg`;
			}

			// Handle AJ1 (Adobe-Japan1) references
			if (entity.startsWith('AJ1-')) {
				const num = entity.substring(4);
				return `https://glyphwiki.org/glyph/aj1-${num}.svg`;
			}

			// Handle GT (GT sources) references
			// Examples: GT-12345 -> gt-12345, GT-K00264 -> gt-k00264
			if (entity.startsWith('GT-')) {
				const suffix = entity.substring(3).toLowerCase(); // Lowercase the entire suffix (handles GT-K)
				return `https://glyphwiki.org/glyph/gt-${suffix}.svg`;
			}

			// Handle itaiji (variant) references
			// Pattern: U-i###+ where ### is the variant number
			// Example: U-i001+20541 -> u20541-itaiji-001
			if (entity.startsWith('U-i')) {
				const match = entity.match(/^U-i(\d+)\+([0-9A-Fa-f]+)$/);
				if (match) {
					const variantNum = match[1]; // e.g., "001"
					const codePoint = match[2].toLowerCase(); // e.g., "20541"
					return `https://glyphwiki.org/glyph/u${codePoint}-itaiji-${variantNum}.svg`;
				}
			}

			// Handle other entity references - try as-is
			return `https://glyphwiki.org/glyph/${entity.toLowerCase()}.svg`;
		}

		// Regular Unicode character
		const codePoint = char.codePointAt(0);
		if (!codePoint) return '';
		const hex = codePoint.toString(16).padStart(4, '0'); // Pad to at least 4 digits
		return `https://glyphwiki.org/glyph/u${hex}.svg`;
	}
</script>

<div class="game-container">
	{#if loading}
		<div class="loading">Loading game data...</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if gameState}
		<!-- Header -->
		<header class="game-header">
			<div class="level-info">HSK Level {gameState.currentLevel}</div>
			<div class="round-info">
				Round {gameState.currentRound}/{gameState.roundsPerLevel}
			</div>
			<div class="hints-counter">💡 Hints used: {gameState.totalHintsUsed}</div>
		</header>

		<!-- Gloss -->
		<div class="gloss-container">
			<div class="gloss-lines">
				{#each gameState.targetGloss.split('; ') as line}
					<div class="gloss-line">{line}</div>
				{/each}
			</div>
			<div class="attempts">Attempts: {gameState.attemptsLeft}/{gameState.maxAttempts}</div>
		</div>

		<!-- Correct Answer Display (shown when won) -->
		{#if gameState.won}
			<div class="answer-display">
				<div class="answer-label">🎉 Correct Answer!</div>
				<img
					src={getGlyphWikiUrl(gameState.targetWord)}
					alt={gameState.targetWord}
					class="answer-glyph"
					onerror={(e) => {
						const target = e.currentTarget as HTMLImageElement;
						target.style.display = 'none';
						const sibling = target.nextElementSibling as HTMLElement;
						if (sibling) sibling.style.display = 'block';
					}}
				/>
				<span class="answer-fallback" style="display: none;">{gameState.targetWord}</span>
			</div>
		{/if}

		<!-- Available Cards -->
		<div class="cards-container">
			<h3>Available Components:</h3>
			<div class="cards">
				{#each gameState.availableCards as card (card.id)}
					<button
						class="card"
						class:selected={gameState.selectedCards.some((c) => c.id === card.id)}
						class:leaf={card.isLeaf}
						class:hinted={highlightedCardIds.has(card.id)}
						onclick={() => toggleCardSelection(card)}
					>
						<img
							src={getGlyphWikiUrl(card.character)}
							alt={card.character}
							class="card-glyph"
							onerror={(e) => {
								e.currentTarget.style.display = 'none';
								e.currentTarget.nextElementSibling.style.display = 'block';
							}}
						/>
						<span class="card-fallback" style="display: none;">{card.character}</span>
					</button>
				{/each}
			</div>
		</div>

		<!-- Possible Combinations -->
		{#if gameState.possibleCombinations.length > 0}
			<div class="combinations-container">
				<h3>Possible Combinations:</h3>
				<div class="combinations">
					{#each gameState.possibleCombinations as combo}
						<button class="combo-button" onclick={() => handleCombine(combo)}>
							<img
								src={getGlyphWikiUrl(combo)}
								alt={combo}
								class="combo-glyph"
								onerror={(e) => {
									e.currentTarget.style.display = 'none';
									e.currentTarget.nextElementSibling.style.display = 'inline';
								}}
							/>
							<span class="combo-fallback" style="display: none;">{combo}</span>
						</button>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Decompose Button (when single card selected) -->
		{#if gameState.selectedCards.length === 1 && !gameState.selectedCards[0].isLeaf}
			<div class="decompose-container">
				<button class="decompose-button" onclick={() => handleDecompose(gameState.selectedCards[0])}>
					Decompose
					<img
						src={getGlyphWikiUrl(gameState.selectedCards[0].character)}
						alt={gameState.selectedCards[0].character}
						class="decompose-glyph"
						onerror={(e) => {
							e.currentTarget.style.display = 'none';
							e.currentTarget.nextElementSibling.style.display = 'inline';
						}}
					/>
					<span class="decompose-fallback" style="display: none;">
						{gameState.selectedCards[0].character}
					</span>
				</button>
			</div>
		{/if}

		<!-- Action Buttons -->
		<div class="actions">
			{#if gameState.won}
				<!-- Show Next Round button when won -->
				<button
					class="action-button next-round-button"
					onclick={handleNextRound}
				>
					Next Round →
				</button>
			{:else}
				<!-- Show normal buttons during gameplay -->
				<button
					class="action-button hint-button"
					onclick={handleHint}
					disabled={gameState.hints.filter(h => !h.used).length === 0 || gameState.gameOver}
				>
					💡 Hint
				</button>
				<button
					class="action-button submit-button"
					onclick={handleSubmit}
					disabled={gameState.gameOver}
				>
					Submit Answer
				</button>
			{/if}
		</div>

		<!-- Message (at bottom so it doesn't shift content) -->
		{#if message}
			<div class="message">{message}</div>
		{/if}

		<!-- Game Over -->
		{#if gameState.gameOver}
			<div class="game-over">
				<button class="reset-button" onclick={resetGame}>Start New Game</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.game-container {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
		padding-bottom: 8rem; /* Space for fixed buttons */
		text-align: center;
		font-family: system-ui, -apple-system, sans-serif;
	}

	.loading,
	.error {
		font-size: 1.5rem;
		padding: 2rem;
	}

	.error {
		color: #dc2626;
	}

	.game-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding: 1rem;
		background: #f3f4f6;
		border-radius: 0.5rem;
	}

	.level-info,
	.round-info,
	.hints-counter {
		font-weight: 600;
		font-size: 1.125rem;
	}

	.hints-counter {
		color: #6366f1;
	}

	.gloss-container {
		margin-bottom: 2rem;
		text-align: left;
	}

	.gloss-lines {
		margin-bottom: 1rem;
	}

	.gloss-line {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: #1f2937;
		line-height: 1.6;
	}

	.gloss-line:first-child {
		font-size: 1.75rem;
		font-weight: 700;
		color: #6366f1;
	}

	.attempts {
		font-size: 1rem;
		color: #6b7280;
	}

	.message {
		padding: 1rem;
		margin-bottom: 1rem;
		background: #dbeafe;
		border-radius: 0.5rem;
		font-weight: 500;
	}

	.combinations-container,
	.decompose-container {
		margin-bottom: 2rem;
	}

	.combinations {
		display: flex;
		gap: 0.5rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.combo-button {
		padding: 0.75rem 1.5rem;
		font-size: 1.5rem;
		background: #10b981;
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 60px;
		min-height: 60px;
	}

	.combo-button:hover {
		background: #059669;
		transform: scale(1.05);
	}

	.combo-glyph {
		width: 40px;
		height: 40px;
		object-fit: contain;
		filter: brightness(0) invert(1); /* Make SVG white */
	}

	.combo-fallback {
		font-size: 1.5rem;
	}

	.decompose-button {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
		background: #f59e0b;
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.decompose-button:hover {
		background: #d97706;
	}

	.decompose-glyph {
		width: 30px;
		height: 30px;
		object-fit: contain;
		filter: brightness(0) invert(1); /* Make SVG white */
	}

	.decompose-fallback {
		font-size: 1rem;
	}


	.decompose-glyph {
		width: 30px;
		height: 30px;
		object-fit: contain;
		filter: brightness(0) invert(1); /* Make SVG white */
	}

	.decompose-fallback {
		font-size: 1rem;
	}

	.cards-container {
		margin-bottom: 2rem;
	}

	.cards {
		display: flex;
		gap: 0.75rem;
		justify-content: center;
		flex-wrap: wrap;
		margin-top: 1rem;
	}

	.card {
		width: 80px;
		height: 80px;
		font-size: 2rem;
		background: white;
		border: 3px solid #d1d5db;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.5rem;
		position: relative;
	}

	.card-glyph {
		width: 100%;
		height: 100%;
		object-fit: contain;
	}

	.card-fallback {
		font-size: 2rem;
	}

	.card:hover {
		border-color: #3b82f6;
		transform: translateY(-2px);
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.card.selected {
		background: #3b82f6;
		color: white;
		border-color: #2563eb;
	}

	.card.leaf {
		border-color: #10b981;
	}

	.card.hinted {
		border-color: #fbbf24;
		border-width: 4px;
		box-shadow: 0 0 12px rgba(251, 191, 36, 0.5);
		animation: pulse-hint 1.5s ease-in-out infinite;
	}

	@keyframes pulse-hint {
		0%,
		100% {
			box-shadow: 0 0 12px rgba(251, 191, 36, 0.5);
		}
		50% {
			box-shadow: 0 0 20px rgba(251, 191, 36, 0.8);
		}
	}

	.actions {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		gap: 1rem;
		justify-content: center;
		padding: 1.5rem;
		background: white;
		border-top: 2px solid #e5e7eb;
		box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.05);
		z-index: 10;
	}

	.action-button {
		padding: 0.75rem 2rem;
		font-size: 1.125rem;
		font-weight: 600;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.hint-button {
		background: #8b5cf6;
		color: white;
	}

	.hint-button:hover {
		background: #7c3aed;
	}

	.submit-button {
		background: #3b82f6;
		color: white;
	}

	.submit-button:hover:not(:disabled) {
		background: #2563eb;
	}

	.submit-button:disabled {
		background: #9ca3af;
		cursor: not-allowed;
	}

	.next-round-button {
		background: #10b981;
		color: white;
		font-size: 1.25rem;
		padding: 1rem 2rem;
		max-width: 400px;
		width: 100%;
	}

	.next-round-button:hover {
		background: #059669;
	}

	.answer-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem;
		margin: 2rem 0;
		background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
		border-radius: 1rem;
		border: 3px solid #fbbf24;
	}

	.answer-label {
		font-size: 1.5rem;
		font-weight: 700;
		color: #92400e;
		margin-bottom: 1.5rem;
	}

	.answer-glyph {
		width: 200px;
		height: 200px;
		object-fit: contain;
	}

	.answer-fallback {
		font-size: 10rem;
		font-weight: 700;
		color: #1f2937;
	}

	.game-over {
		margin-top: 2rem;
	}

	.reset-button {
		padding: 1rem 2rem;
		font-size: 1.25rem;
		font-weight: 600;
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.reset-button:hover {
		background: #b91c1c;
	}
</style>