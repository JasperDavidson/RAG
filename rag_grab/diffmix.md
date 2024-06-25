// Used for mixing

module diffmix_25px_0 (
    input soln1,
    input soln2,
    output out_fluid
);
    assign out_fluid = soln1 + soln2;

endmodule