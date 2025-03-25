function mostrarReceta(nombre) {
    const recetas = {
    "Galleta de Brownie": `
        **Ingredientes:**  
        - 1 taza de harina  
        - 1/2 taza de cacao en polvo  
        - 1 taza de azúcar  
        - 1/2 taza de mantequilla derretida  
        - 2 huevos  
        - 1/2 cucharadita de esencia de vainilla  
        - 1/4 cucharadita de sal  

        **Instrucciones:**  
        1. Mezcla la harina, el cacao, el azúcar y la sal en un recipiente.  
        2. Agrega la mantequilla derretida, los huevos y la esencia de vainilla. Mezcla bien.  
        3. Coloca cucharadas de la mezcla en una bandeja con papel para hornear.  
        4. Hornea a 180°C por 12-15 minutos.  

        ¡Disfruta tus galletas de brownie!
    `,
    "Galleta Mamut": `
        **Ingredientes:**  
        - 1 taza de harina  
        - 1/2 taza de azúcar  
        - 1/4 taza de mantequilla  
        - 1/4 taza de leche  
        - 1/2 taza de malvaviscos  
        - 1/2 taza de chocolate derretido  

        **Instrucciones:**  
        1. Mezcla la harina, el azúcar, la mantequilla y la leche hasta formar una masa.  
        2. Haz galletas planas y hornéalas a 180°C por 10 minutos.  
        3. Coloca un malvavisco sobre cada galleta caliente.  
        4. Baña las galletas con el chocolate derretido y deja enfriar.  

        ¡Disfruta tus galletas tipo Mamut!
    `,
    "Galleta Oreo": `
        **Ingredientes:**  
        - 1 taza de harina  
        - 1/2 taza de cacao en polvo  
        - 1/2 taza de azúcar  
        - 1/2 taza de mantequilla  
        - 1 huevo  
        - 1/2 cucharadita de esencia de vainilla  
        - Una pizca de sal  

        **Para el relleno:**  
        - 1/2 taza de azúcar glas  
        - 1/4 taza de mantequilla  
        - 1/2 cucharadita de esencia de vainilla  

        **Instrucciones:**  
        1. Mezcla harina, cacao, azúcar y sal. Agrega mantequilla, huevo y vainilla; forma una masa.  
        2. Extiende y corta círculos pequeños. Hornea a 180°C por 10-12 minutos.  
        3. Para el relleno, bate la mantequilla, azúcar glas y vainilla hasta que esté suave.  
        4. Rellena las galletas una vez frías y presiona suavemente para juntar cada par.  

        ¡Disfruta tus galletas tipo Oreo caseras!
    `,
    "Galleta de Mantequilla": `
        **Ingredientes:**  
        - 2 tazas de harina  
        - 1/2 taza de azúcar  
        - 1 taza de mantequilla  
        - 1 cucharadita de esencia de vainilla  
        - Una pizca de sal  

        **Instrucciones:**  
        1. Mezcla la mantequilla, el azúcar y la esencia de vainilla hasta que esté cremoso.  
        2. Añade la harina y la sal poco a poco hasta formar una masa.  
        3. Extiende y corta las galletas.  
        4. Hornea a 180°C por 10-12 minutos.  

        ¡Disfruta tus galletas de mantequilla!
    `,
    "Galleta Alfajores": `
        **Ingredientes:**  
        - 1 taza de harina  
        - 1/2 taza de maicena  
        - 1/2 taza de mantequilla  
        - 1/4 taza de azúcar  
        - 1 cucharadita de esencia de vainilla  
        - 1 taza de dulce de leche  

        **Instrucciones:**  
        1. Mezcla la mantequilla, el azúcar y la esencia de vainilla hasta que esté cremoso.  
        2. Añade la harina y la maicena poco a poco hasta formar una masa.  
        3. Extiende y corta las galletas. Hornea a 180°C por 8-10 minutos.  
        4. Une las galletas con dulce de leche y decora con coco rallado si deseas.  

        ¡Disfruta tus alfajores caseros!
    `,
    "Galleta con Chispas de Chocolate": `
        **Ingredientes:**  
        - 2 tazas de harina  
        - 1/2 taza de azúcar  
        - 1/2 taza de azúcar morena  
        - 1 taza de mantequilla  
        - 1 huevo  
        - 1 cucharadita de esencia de vainilla  
        - 1 taza de chispas de chocolate  

        **Instrucciones:**  
        1. Mezcla la mantequilla, los azúcares, el huevo y la esencia de vainilla.  
        2. Agrega la harina y mezcla bien. Incorpora las chispas de chocolate.  
        3. Forma bolitas y colócalas en una bandeja con papel para hornear.  
        4. Hornea a 180°C por 10-12 minutos.  

        ¡Disfruta tus galletas con chispas de chocolate!
    `,
    "Galleta de Avena": `
        **Ingredientes:**  
        - 1 taza de avena  
        - 1 taza de harina  
        - 1/2 taza de azúcar  
        - 1/2 taza de mantequilla  
        - 1 huevo  
        - 1/2 cucharadita de canela en polvo  

        **Instrucciones:**  
        1. Mezcla la avena, la harina, el azúcar y la canela.  
        2. Agrega la mantequilla derretida y el huevo. Mezcla bien.  
        3. Haz bolitas y aplánalas en una bandeja con papel para hornear.  
        4. Hornea a 180°C por 10-12 minutos.  

        ¡Disfruta tus galletas de avena!
    `,
    "Galleta Florentina": `
        **Ingredientes:**  
        - 1/2 taza de almendras fileteadas  
        - 1/4 taza de miel  
        - 1/4 taza de azúcar  
        - 1/4 taza de mantequilla  
        - 1/4 taza de harina  

        **Instrucciones:**  
        1. Mezcla la miel, el azúcar, la mantequilla y la harina. Cocina a fuego lento hasta que espese.  
        2. Agrega las almendras fileteadas y mezcla bien.  
        3. Coloca cucharadas de la mezcla en una bandeja con papel para hornear.  
        4. Hornea a 180°C por 8-10 minutos.  

        ¡Disfruta tus galletas florentinas!
    `,
        "Galleta Don Galleto": `
**Ingredientes:**
- 5 kg de harina de trigo  
- 2.5 kg de mantequilla sin sal (a temperatura ambiente)  
- 2.5 kg de azúcar (puedes usar azúcar blanca, morena o una combinación)  
- 5 kg de nueces troceadas  
- 1 litro de leche  
- 50 g de sal  
- 50 g de polvo para hornear  
- 20 g de esencia de vainilla  

**Procedimiento:**
1. Precalienta el horno a 180°C (350°F).  
2. Tamiza la harina, el polvo para hornear y la sal en un tazón grande.  
3. Bate la mantequilla y el azúcar en otro tazón hasta obtener una mezcla cremosa.  
4. Añade la esencia de vainilla y continúa batiendo.  
5. Incorpora la mezcla de harina poco a poco, alternando con la leche, hasta que se forme una masa uniforme.  
6. Añade las nueces troceadas y mezcla bien.  
7. Forma bolitas de masa del tamaño deseado (aproximadamente 30-40 gramos cada una).  
8. Coloca las bolitas en una bandeja para hornear, dejando espacio entre ellas para que se expandan durante el horneado.  
9. Hornea las galletas durante 12-15 minutos o hasta que estén doradas en los bordes.  
10. Deja enfriar las galletas en una rejilla antes de servir.  

¡Disfruta las deliciosas Galletas "Sorpresa Nuez Don Galleto"!
`,

    "Galleta de Almendra": `
        **Ingredientes:**  
        - 1 taza de harina de almendra  
        - 1/4 taza de azúcar glas  
        - 1/4 taza de mantequilla  
        - 1 huevo  

        **Instrucciones:**  
        1. Mezcla todos los ingredientes hasta formar una masa.  
        2. Haz bolitas y aplánalas ligeramente.  
        3. Coloca en una bandeja con papel para hornear.  
        4. Hornea a 180°C por 10-12 minutos.  

        ¡Disfruta tus galletas de almendra!
    `
    
};
}
