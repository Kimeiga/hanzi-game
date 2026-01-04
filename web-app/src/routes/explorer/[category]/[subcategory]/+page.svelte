<script lang="ts">
	import type { PageData } from './$types';

	interface CharNode {
		char: string;
		simp: string | null;
		keyword: string;
		pinyin: string;
		meaning: string;
		study_order: number;
	}

	interface TreeNode {
		name: string;
		children?: (TreeNode | CharNode)[];
	}

	// Server-loaded data
	let { data } = $props<{ data: PageData }>();

	const categoryColors: Record<string, string> = {
		nature: '#22c55e',
		human: '#3b82f6',
		society: '#8b5cf6',
		objects: '#f59e0b',
		abstract: '#6366f1',
		communication: '#ec4899'
	};

	function isCharNode(node: TreeNode | CharNode): node is CharNode {
		return 'char' in node;
	}

	function countChars(node: TreeNode | CharNode): number {
		if (isCharNode(node)) return 1;
		return node.children?.reduce((sum, c) => sum + countChars(c), 0) ?? 0;
	}

	// Find category and subcategory in the graph
	let categoryData = $derived.by(() => {
		const treeData = data.semanticGraph as TreeNode;
		if (!treeData?.children) return null;
		return treeData.children.find(
			(c): c is TreeNode => !isCharNode(c) && c.name.toLowerCase() === data.categoryName
		) || null;
	});

	let subcategoryData = $derived.by(() => {
		if (!categoryData?.children) return null;
		return categoryData.children.find(
			(c): c is TreeNode => !isCharNode(c) && c.name.toLowerCase() === data.subcategoryName
		) || null;
	});

	let chars = $derived.by(() => {
		if (!subcategoryData?.children) return [];
		return subcategoryData.children.filter((c): c is CharNode => isCharNode(c));
	});

	let subcategories = $derived.by(() => {
		if (!subcategoryData?.children) return [];
		return subcategoryData.children.filter((c): c is TreeNode => !isCharNode(c));
	});
</script>

<div class="explorer-container">
	<nav class="breadcrumb">
		<a href="/explorer">Hanzi Universe</a>
		<span class="separator">›</span>
		<a href="/explorer/{data.categoryName}">{categoryData?.name || data.categoryName}</a>
		<span class="separator">›</span>
		<span class="current">{subcategoryData?.name || data.subcategoryName}</span>
	</nav>

	{#if subcategoryData}
		<header class="category-header" style="--cat-color: {categoryColors[data.categoryName] || '#64748b'}">
			<h1>{subcategoryData.name}</h1>
			<p class="char-count">{countChars(subcategoryData)} characters</p>
		</header>

		{#if subcategories.length > 0}
			<section class="subcategories">
				<h2>Subcategories</h2>
				<div class="subcat-grid">
					{#each subcategories as subcat}
						<a
							href="/explorer/{data.categoryName}/{data.subcategoryName}/{subcat.name.toLowerCase()}"
							class="subcat-card"
							style="--cat-color: {categoryColors[data.categoryName] || '#64748b'}"
						>
							<span class="subcat-name">{subcat.name}</span>
							<span class="subcat-count">{countChars(subcat)} characters</span>
						</a>
					{/each}
				</div>
			</section>
		{/if}

		{#if chars.length > 0}
			<section class="direct-chars">
				{#if subcategories.length > 0}
					<h2>Other Characters</h2>
				{/if}
				<div class="char-grid">
					{#each chars as char (char.char)}
						<a href="/character/{encodeURIComponent(char.char)}" class="char-card">
							<span class="char">{char.char}</span>
							{#if char.simp && char.simp !== char.char}
								<span class="simp">({char.simp})</span>
							{/if}
							<span class="keyword">{char.keyword}</span>
							{#if char.pinyin}
								<span class="pinyin">{char.pinyin}</span>
							{/if}
						</a>
					{/each}
				</div>
			</section>
		{/if}
	{:else}
		<div class="error">Subcategory "{data.subcategoryName}" not found</div>
	{/if}

	<a href="/explorer/{data.categoryName}" class="back-link">← Back to {categoryData?.name || data.categoryName}</a>
</div>

<style>
	.explorer-container { min-height: 100vh; background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); color: #e2e8f0; padding: 2rem; font-family: system-ui, -apple-system, sans-serif; }
	.breadcrumb { margin-bottom: 1.5rem; font-size: 0.875rem; }
	.breadcrumb a { color: #60a5fa; text-decoration: none; }
	.breadcrumb a:hover { text-decoration: underline; }
	.separator { color: #64748b; margin: 0 0.5rem; }
	.current { color: #94a3b8; }
	.category-header { margin-bottom: 2rem; }
	.category-header h1 { font-size: 2.5rem; font-weight: 700; color: var(--cat-color, #e2e8f0); margin-bottom: 0.25rem; }
	.char-count { color: #94a3b8; }

	/* Subcategories section */
	.subcategories { margin-bottom: 2rem; }
	.subcategories h2 { font-size: 1.25rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 600; }
	.subcat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
	.subcat-card { display: flex; flex-direction: column; padding: 1.25rem; background: #1e293b; border: 2px solid #334155; border-radius: 0.75rem; text-decoration: none; transition: all 0.2s; }
	.subcat-card:hover { border-color: var(--cat-color, #60a5fa); background: #334155; transform: translateY(-2px); }
	.subcat-name { font-size: 1.125rem; font-weight: 600; color: var(--cat-color, #e2e8f0); margin-bottom: 0.25rem; }
	.subcat-count { font-size: 0.875rem; color: #64748b; }

	/* Direct characters section */
	.direct-chars { margin-bottom: 2rem; }
	.direct-chars h2 { font-size: 1.25rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 600; }

	.char-grid { display: flex; flex-wrap: wrap; gap: 1rem; padding-bottom: 5rem; }
	.char-card { display: flex; flex-direction: column; align-items: center; padding: 1rem; background: #1e293b; border: 1px solid #334155; border-radius: 0.5rem; min-width: 100px; transition: all 0.2s; text-decoration: none; color: inherit; }
	.char-card:hover { border-color: #60a5fa; background: #334155; transform: translateY(-2px); }
	.char { font-size: 2.5rem; line-height: 1; margin-bottom: 0.5rem; }
	.simp { font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem; }
	.keyword { font-size: 0.75rem; font-weight: 600; color: #60a5fa; text-align: center; }
	.pinyin { font-size: 0.625rem; color: #a78bfa; margin-top: 0.25rem; }
	.loading, .error { text-align: center; padding: 4rem; }
	.error { color: #f87171; }
	.back-link { position: fixed; bottom: 2rem; left: 2rem; color: #60a5fa; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; background: #1e293b; border-radius: 0.5rem; border: 2px solid #334155; }
	.back-link:hover { background: #334155; border-color: #60a5fa; }
</style>
