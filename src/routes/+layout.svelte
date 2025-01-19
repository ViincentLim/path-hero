<script lang="ts">
    import '../app.postcss';
</script>

<div>
    <slot/>
</div>

<style>
    /*:global(.dark [data-theme='hamlindigo']) {*/
    /*  background-image: None!important;*/
    /*}*/
    :global(.dark body) {
        background: white !important;
    }

    :global(.card) {
        border: 1px solid black !important;
        border-radius: 12px;
    }

    :global(input::placeholder) {
        color: gray!important;
        font-style: italic;
        text-align: center;
    }
</style>