describe("API de pedidos de la pastelería", () => {
  const fechaPrueba = "2026-12-20";

  it("crea un pedido y lo consulta por fecha", () => {
    const pedido = {
      cliente: "Cliente Cypress",
      tipoPastel: "Pastel de chocolate",
      porciones: 20,
      decoracion: "Cumpleaños",
      fechaEntrega: fechaPrueba,
      horaEntrega: "17:30",
      tiempoPreparacion: 180,
      estado: "pendiente"
    };

    cy.request({
      method: "POST",
      url: "/pedidos",
      body: pedido
    }).then((respuestaPost) => {
      expect(respuestaPost.status).to.eq(201);

      expect(respuestaPost.body.mensaje).to.eq(
        "Pedido registrado correctamente"
      );

      expect(respuestaPost.body.pedido)
        .to.have.property("id");

      expect(respuestaPost.body.pedido.cliente)
        .to.eq(pedido.cliente);
    });

    cy.request(`/pedidos/fecha/${fechaPrueba}`)
      .then((primeraConsulta) => {
        expect(primeraConsulta.status).to.eq(200);

        expect(primeraConsulta.body.fecha)
          .to.eq(fechaPrueba);

        expect(primeraConsulta.body.cantidad)
          .to.be.greaterThan(0);

        expect(primeraConsulta.body.pedidos)
          .to.be.an("array");

        expect(primeraConsulta.body.cache)
          .to.eq("MISS");

        expect(primeraConsulta.headers["x-cache"])
          .to.eq("MISS");
      });

    cy.request(`/pedidos/fecha/${fechaPrueba}`)
      .then((segundaConsulta) => {
        expect(segundaConsulta.status).to.eq(200);

        expect(segundaConsulta.body.cache)
          .to.eq("HIT");

        expect(segundaConsulta.headers["x-cache"])
          .to.eq("HIT");
      });
  });

  it("rechaza un pedido con información incompleta", () => {
    cy.request({
      method: "POST",
      url: "/pedidos",
      failOnStatusCode: false,
      body: {
        tipoPastel: "Pastel de vainilla",
        porciones: 10
      }
    }).then((respuesta) => {
      expect(respuesta.status).to.eq(400);

      expect(respuesta.body.error)
        .to.eq("Faltan campos obligatorios");

      expect(respuesta.body.campos)
        .to.include("cliente");
    });
  });
});